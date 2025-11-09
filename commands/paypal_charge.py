# commands/paypal_charge.py
import sys
import os
import time
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_credits, set_credits, get_plan, is_premium
from utils.bin_database import get_bin_info
from config import ADMIN_ID
from config import get_random_proxy

def setup_paypal_charge_command(bot):
    @bot.message_handler(commands=['pp'])
    def paypal_charge_command(message):
        process_paypal_charge(bot, message)
    
    @bot.message_handler(func=lambda message: message.text and message.text.startswith('.pp '))
    def paypal_charge_command_dot(message):
        process_paypal_charge(bot, message)

def process_paypal_charge(bot, message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    # SOLO PARA USUARIOS PREMIUM
    if not is_premium(user_id):
        bot.reply_to(message, "❌ Comando solo para usuarios premium.\n💎 Contacta a @Dunxito para adquirir tu plan.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Uso: `/pp cc|mm|aa|cvv`\nEjemplo: `/pp 4104886655308541|09|29|094`", parse_mode="Markdown")
            return
        
        card_data = parts[1]
        
        # Verificar formato de tarjeta
        if '|' not in card_data:
            bot.reply_to(message, "❌ Formato incorrecto. Use: `/pp cc|mm|aa|cvv`", parse_mode="Markdown")
            return
        
        card_parts = card_data.split('|')
        if len(card_parts) != 4:
            bot.reply_to(message, "❌ Formato incorrecto. Use: `/pp cc|mm|aa|cvv`", parse_mode="Markdown")
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
        processing_msg = bot.reply_to(message, "🔄 Procesando PayPal 1$ Charge...\n⏳ Esto puede tomar hasta 40 segundos...")
        
        # URL para PayPal Charge
        proxy = get_random_proxy()
        paypal_url = f"https://paypal-0mqq.onrender.com/charge/test/{cc_number}|{expiry_month}|{formatted_year}|{cvv}"
        
        # Hacer la solicitud con timeout de 40 segundos
        start_time = time.time()
        response = make_simple_request(paypal_url)
        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        
        # Procesar la respuesta JSON
        result_message = extract_paypal_response(response)
        status = get_paypal_status(response)
        
        # Obtener información del BIN
        bin_info = get_bin_info(cc_number[:6])
        
        # Obtener plan del usuario
        credits = get_credits(user_id)
        plan = get_plan(user_id, credits)
        
        # Eliminar mensaje de procesamiento
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        # FORMATEAR RESPUESTA CON NUEVO FORMATO
        response_text = f"""Kirio | PayPal
━━━━━━━━━━━━━
𝗖𝗮𝗿𝗱 ➔ {cc_number}|{expiry_month}|{expiry_year}|{cvv}
𝗦𝘁𝗮𝘁𝘂𝘀 ➔ {status}
𝗥𝗲𝘀𝘂𝗹𝘁 ➔ {result_message}
━━━━━━━━━━━━━
𝗕𝗮𝗻𝗸 ➙ {bin_info.get('bank', 'UNKNOWN BANK')}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ➙ {bin_info.get('country', 'UNKNOWN')} | {bin_info.get('emoji', '🏳️')}
𝗜𝗻𝗳𝗼 ➙ {bin_info.get('brand', 'UNKNOWN')} {bin_info.get('type', '')}
━━━━━━━━━━━━━
𝗧𝗶𝗺𝗲 ➙ {processing_time}s
━━━━━━━━━━━━━
𝗗𝗲𝘃 ➙ Dunxito
𝗖𝗵𝗲𝗰𝗸 𝗕𝘆 ➙ {username} [{plan}]
━━━━━━━━━━━━━
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
    """Hace una solicitud simple con requests - TIMEOUT 40 SEGUNDOS"""
    try:
        response = requests.get(url, timeout=90)  # ← AUMENTADO A 40 SEGUNDOS
        # Verificar si la respuesta está vacía
        if not response.text.strip():
            return "EMPTY_RESPONSE"
        return response.text
    except requests.exceptions.Timeout:
        return "TIMEOUT_ERROR"
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR"
    except requests.exceptions.RequestException as e:
        return f"NETWORK_ERROR: {str(e)}"
    except Exception as e:
        return f"UNKNOWN_ERROR: {str(e)}"

def extract_paypal_response(response):
    """Extrae el mensaje específico para PayPal"""
    # Si la respuesta está vacía o es un error
    if not response or any(error in response for error in ["TIMEOUT_ERROR", "CONNECTION_ERROR", "NETWORK_ERROR", "EMPTY_RESPONSE"]):
        return response.replace("_", " ") if response else "NO_RESPONSE"
    
    try:
        data = json.loads(response)
        if "response" in data:
            return data["response"]
        elif "message" in data:
            return data["message"]
        elif "error" in data:
            return data["error"]
        elif "result" in data:
            return data["result"]
        else:
            # Si no hay campo específico, intentar mostrar algo útil
            for key in ['status', 'info', 'gateway', 'reason']:
                if key in data:
                    return str(data[key])
            return "UNKNOWN_RESPONSE_FORMAT"
    except json.JSONDecodeError:
        # Si no es JSON, devolver la respuesta directa (limitada)
        if "approved" in response.lower():
            return "APPROVED"
        elif "declined" in response.lower():
            return "DECLINED"
        elif "error" in response.lower():
            return "ERROR"
        else:
            return response[:50] + "..." if len(response) > 50 else response

def get_paypal_status(response):
    """Determina el estado específico para PayPal"""
    # Si la respuesta está vacía o es error de red
    if not response:
        return "NO_RESPONSE ⚠️"
    if any(error in response for error in ["TIMEOUT_ERROR", "CONNECTION_ERROR", "NETWORK_ERROR"]):
        return "NETWORK_ERROR ⚠️"
    if "EMPTY_RESPONSE" in response:
        return "EMPTY_RESPONSE ⚠️"
    
    try:
        data = json.loads(response)
        status = data.get("status", "").lower()
        
        if status == "approved" or status == "success":
            return "Approved! ✅"
        elif status == "declined" or status == "failed":
            return "Declined! ❌"
        else:
            # Buscar status en otros campos
            for field in ['result', 'message', 'response']:
                if field in data and any(word in str(data[field]).lower() for word in ['approved', 'success']):
                    return "Approved! ✅"
                if field in data and any(word in str(data[field]).lower() for word in ['declined', 'failed', 'error']):
                    return "Declined! ❌"
            return "Pending 🔄"
            
    except json.JSONDecodeError:
        # Si no es JSON, buscar palabras clave en el texto
        response_lower = response.lower()
        if "approved" in response_lower or "success" in response_lower:
            return "Approved! ✅"
        elif "declined" in response_lower or "failed" in response_lower:
            return "Declined! ❌"
        elif "error" in response_lower:
            return "Error! ⚠️"
        else:
            return "Unknown 🔄"