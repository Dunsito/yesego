# commands/braintree_ccn.py
import sys
import os
import time
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_credits, set_credits, get_plan, is_premium, increment_daily_usage, can_use_free_command
from utils.bin_database import get_bin_info
from config import ADMIN_ID

def setup_braintree_ccn_command(bot):
    @bot.message_handler(commands=['b3'])
    def braintree_ccn_command(message):
        process_braintree_ccn(bot, message)
    
    @bot.message_handler(func=lambda message: message.text and message.text.startswith('.b3 '))
    def braintree_ccn_command_dot(message):
        process_braintree_ccn(bot, message)

def process_braintree_ccn(bot, message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    # Verificar límite diario para Free Users (30 usos)
    can_use, remaining = can_use_free_command(user_id)
    if not can_use:
        bot.reply_to(message, f"❌ Límite diario alcanzado.\n📊 Has usado tus 30 usos gratuitos hoy.\n⏰ El límite se reinicia a las 12:00 AM.\n💎 Obtén Premium para uso ilimitado.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Uso: `/b3 cc|mm|aa|cvv`\nEjemplo: `/b3 4104886655308541|09|29|094`", parse_mode="Markdown")
            return
        
        card_data = parts[1]
        
        # Verificar formato de tarjeta
        if '|' not in card_data:
            bot.reply_to(message, "❌ Formato incorrecto. Use: `/b3 cc|mm|aa|cvv`", parse_mode="Markdown")
            return
        
        card_parts = card_data.split('|')
        if len(card_parts) != 4:
            bot.reply_to(message, "❌ Formato incorrecto. Use: `/b3 cc|mm|aa|cvv`", parse_mode="Markdown")
            return
        
        cc_number, expiry_month, expiry_year, cvv = card_parts
        
        # Validar datos
        if not (cc_number.isdigit() and len(cc_number) == 16):
            bot.reply_to(message, "❌ Número de tarjeta inválido. Debe tener 16 dígitos")
            return
            
        if not (expiry_month.isdigit() and 1 <= int(expiry_month) <= 12):
            bot.reply_to(message, "❌ Mes de expiración inválido. Use 01-12")
            return
            
        # Validar y formatear año
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
            bot.reply_to(message, "❌ Año de expiración inválido. Use 1, 2 o 4 dígitos (ej: 9, 29 o 2029)")
            return
            
        if not (cvv.isdigit() and len(cvv) in [3, 4]):
            bot.reply_to(message, "❌ CVV inválido. Debe tener 3 o 4 dígitos")
            return
        
        # Enviar mensaje de procesamiento
        processing_msg = bot.reply_to(message, "🔄 Procesando tu tarjeta en Braintree...")
        
        # URL para Braintree CCN
        braintree_url = f"https://componential-unstruggling-shantel.ngrok-free.dev//check_cc?cc={cc_number}|{expiry_month}|{formatted_year}|{cvv}&email=wasdark336@gmail.com&password=bbmEZs65p!BJLNz"
        
        # Hacer la solicitud simple con requests
        start_time = time.time()
        response = make_simple_request(braintree_url)
        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        
        # Incrementar contador diario solo para Free Users
        if not is_premium(user_id):
            new_count = increment_daily_usage(user_id)
            remaining_after = max(0, 30 - new_count)
            usage_line = f"🔄 𝐔𝐬𝐨𝐬 𝐡𝐨𝐲: {remaining_after}/30"
        else:
            remaining_after = "∞"
            usage_line = ""  # Ocultar para usuarios Premium
        
        # Procesar la respuesta JSON
        result_message = extract_message_from_response(response)
        status = get_status_from_response(response)
        
        # Obtener información del BIN
        bin_info = get_bin_info(cc_number[:6])
        
        # Obtener plan del usuario
        credits = get_credits(user_id)
        plan = get_plan(user_id, credits)
        
        # Eliminar mensaje de procesamiento
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        # Formatear respuesta ordenada - NUEVO FORMATO
        response_text = f"""
- - - - - - - - - - - - - - - - - - - - -
#Meliodas | Braintree_CCN
- - - - - - - - - - - - - - - - - - - - - 
🝮 Card : {cc_number}|{expiry_month}|{expiry_year}|{cvv}
🝮 Status : {status}
🝮 Result : {result_message}
- - - - - - - - - - - - - - - - - - - - -
🝮 Bin : {bin_info.get('scheme', 'UNKNOWN')} | {bin_info.get('brand', 'UNKNOWN')}
🝮 Bank : {bin_info.get('bank', 'UNKNOWN BANK')}
🝮 Country : {bin_info.get('country', 'UNKNOWN')} {bin_info.get('emoji', '🏳️')}
- - - - - - - - - - - - - - - - - - - - -
🝮 Proxy : Live ✅ | Retry: 0
🝮 Time : {processing_time}s
🝮 Checked by : {username} [{plan}]
- - - - - - - - - - - - - - - - - - - - -
"""
        
        bot.reply_to(message, response_text)
        
    except Exception as e:
        # Eliminar mensaje de procesamiento si existe
        try:
            if 'processing_msg' in locals():
                bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
        bot.reply_to(message, f"❌ Error: {str(e)}")

def make_simple_request(url):
    """Hace una solicitud simple con requests"""
    try:
        response = requests.get(url, timeout=30)
        return response.text
    except Exception as e:
        return f"Request Error: {str(e)}"

def extract_message_from_response(response):
    """Extrae el mensaje del JSON de respuesta"""
    try:
        data = json.loads(response)
        if "response" in data:
            return data["response"]
        elif "error" in data:
            return data["error"]
        elif "message" in data:
            return data["message"]
        else:
            return response[:100]
    except:
        return response[:100] if response else "NO RESPONSE"

def get_status_from_response(response):
    """Determina el estado basado en la respuesta"""
    try:
        data = json.loads(response)
        status = data.get("status", "").lower()
        
        if status == "approved" or "approved" in str(data.get("response", "")).lower():
            return "Approved"
        elif status == "declined" or "declined" in str(data.get("response", "")).lower():
            return "Declined"
        elif "cannot authorize" in str(data.get("response", "")).lower():
            return "Declined"
        else:
            return "Unknown"
            
    except:
        if "approved" in response.lower():
            return "Approved"
        elif "declined" in response.lower() or "cannot authorize" in response.lower():
            return "Declined"
        else:
            return "Unknown"