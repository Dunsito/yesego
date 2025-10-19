# commands/vbv_checker.py
import sys
import os
import time
import requests
import json
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_credits, set_credits, get_plan, is_premium, increment_daily_usage, can_use_free_command
from utils.bin_database import get_bin_info
from config import ADMIN_ID

def make_simple_request(url, max_retries=3):
    """Hacer solicitud HTTP simple con reintentos"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            return response.text
        except requests.exceptions.Timeout:
            print(f"🔹 Timeout en intento {attempt + 1}")
            time.sleep(1)
        except Exception as e:
            print(f"🔹 Error en request: {e}")
            break
    return None

def extract_vbv_status(response_text):
    """Extrae solo el estado VBV para el formato nuevo"""
    if not response_text:
        return "No Response"
    
    try:
        data = json.loads(response_text)
        
        if 'status' in data:
            status = data['status']
            if status.lower() in ['approved', 'success', 'live']:
                return "APPROVED ✅"
            elif status.lower() in ['declined', 'failed', 'die']:
                return "DECLINED ❌"
            else:
                return status.upper()
        
        if 'message' in data:
            return data['message']
            
        if 'response' in data:
            return data['response']
            
        return "Unknown Response"
        
    except json.JSONDecodeError:
        if "approved" in response_text.lower() or "success" in response_text.lower():
            return "APPROVED ✅"
        elif "declined" in response_text.lower() or "failed" in response_text.lower():
            return "DECLINED ❌"
        elif "challenge" in response_text.lower():
            return "Challenge Required"
        else:
            return "Unknown"

def setup_vbv_command(bot):
    @bot.message_handler(commands=['vbv'])
    def vbv_command(message):
        print(f"🔹 Comando /vbv recibido de {message.from_user.first_name}")
        process_vbv_check(bot, message)
    
    @bot.message_handler(func=lambda message: message.text and message.text.startswith('.vbv '))
    def vbv_command_dot(message):
        print(f"🔹 Comando .vbv recibido de {message.from_user.first_name}")
        process_vbv_check(bot, message)

def process_vbv_check(bot, message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    print(f"🔹 Procesando VBV check para {username}")
    
    # Verificar límite diario para Free Users (30 usos)
    can_use, remaining = can_use_free_command(user_id)
    print(f"🔹 Límite diario: {can_use}, Usos restantes: {remaining}")
    
    if not can_use:
        bot.reply_to(message, f"❌ Límite diario alcanzado.\n📊 Has usado tus 30 usos gratuitos hoy.\n⏰ El límite se reinicia a las 12:00 AM.\n💎 Obtén Premium para uso ilimitado.")
        return
    
    try:
        parts = message.text.split()
        print(f"🔹 Partes del mensaje: {parts}")
        
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Uso: `/vbv cc|mm|aa|cvv`\nEjemplo: `/vbv 4673628288456227|01|28|925`", parse_mode="Markdown")
            return
        
        card_data = parts[1]
        print(f"🔹 Datos de tarjeta: {card_data}")
        
        # Verificar formato de tarjeta completa
        if '|' not in card_data:
            bot.reply_to(message, "❌ Formato incorrecto. Use: `/vbv cc|mm|aa|cvv`", parse_mode="Markdown")
            return
        
        card_parts = card_data.split('|')
        if len(card_parts) != 4:
            bot.reply_to(message, "❌ Formato incorrecto. Use: `/vbv cc|mm|aa|cvv`", parse_mode="Markdown")
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
            
        if len(expiry_year) == 2:
            formatted_year = "20" + expiry_year
        elif len(expiry_year) == 4:
            formatted_year = expiry_year
        else:
            bot.reply_to(message, "❌ Año de expiración inválido. Use 2 o 4 dígitos")
            return
            
        if not (cvv.isdigit() and len(cvv) in [3, 4]):
            bot.reply_to(message, "❌ CVV inválido. Debe tener 3 o 4 dígitos")
            return
        
        # Enviar mensaje de procesamiento
        print("🔹 Enviando mensaje de procesamiento...")
        processing_msg = bot.reply_to(message, "🔄 Procesando verificación VBV...")
        
        # URL para VBV Check - solo usa el número de tarjeta
        vbv_url = f"https://rocky-815m.onrender.com/gateway=bin?key=rockysoon&card={cc_number}"
        print(f"🔹 URL: {vbv_url}")
        
        # Hacer la solicitud
        start_time = time.time()
        print("🔹 Haciendo request...")
        response = make_simple_request(vbv_url)
        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        print(f"🔹 Response recibido: {response}")
        
        # Incrementar contador diario solo para Free Users (30 usos)
        if not is_premium(user_id):
            new_count = increment_daily_usage(user_id)
            remaining_after = max(0, 30 - new_count)
            usage_line = f"🔄 𝐔𝐬𝐨𝐬 𝐡𝐨𝐲: {remaining_after}/30"
        else:
            remaining_after = "∞"
            usage_line = ""  # Ocultar para usuarios Premium
        
        # Obtener información del BIN
        bin_info = get_bin_info(cc_number[:6])
        print(f"🔹 Info BIN: {bin_info}")
        
        # Obtener créditos y plan del usuario
        credits = get_credits(user_id)
        user_plan = get_plan(user_id, credits)
        
        # Construir mensaje de respuesta con nuevo formato
        response_message = f"""
▬▬▬▬▬⌁・⌁▬▬▬▬▬
カ 𝐂𝐚𝐫𝐝: {cc_number}|{expiry_month}|{expiry_year}|{cvv}
❀ 𝐕𝐁𝐕: {extract_vbv_status(response)}
┄┄┄┄┄┄┄┄┄┄┄┄┄┄
✿ 𝑻𝒚𝒑𝒆 ➜ {bin_info.get('type', 'UNKNOWN')}
✿ 𝑳𝒆𝒗𝒆𝒍 ➜ {bin_info.get('brand', 'UNKNOWN')}
✿ 𝑩𝒂𝒏𝒌 ➜ {bin_info.get('bank', 'UNKNOWN BANK')}
✿ 𝑪𝒐𝒖𝒏𝒕𝒓𝒚 ➜ {bin_info.get('country', 'UNKNOWN')} {bin_info.get('emoji', '🏳️')}
▬▬▬▬▬⌁・⌁▬▬▬▬▬
⏱ 𝐓𝐢𝐦𝐞: {processing_time}s
👤 𝐔𝐬𝐞𝐫: {username} [{user_plan}]
{usage_line}
"""
        
        # Editar el mensaje de procesamiento con el resultado
        bot.edit_message_text(
            chat_id=processing_msg.chat.id,
            message_id=processing_msg.message_id,
            text=response_message,
            parse_mode="Markdown"
        )
        
        print(f"🔹 Verificación VBV completada para {username}")
        
    except Exception as e:
        print(f"🔹 Error en process_vbv_check: {e}")
        error_msg = f"❌ Error al procesar la verificación: {str(e)}"
        try:
            bot.reply_to(message, error_msg)
        except:
            # Si no se puede responder, intentar enviar mensaje nuevo
            bot.send_message(message.chat.id, error_msg)