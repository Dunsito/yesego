# commands/start.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telebot import types
from utils.database import get_credits, get_plan, is_premium, can_use_free_command
from config import ADMIN_ID

# ⬇️⬇️⬇️ ELIMINAR ESTAS LÍNEAS QUE CAUSAN EL IMPORT CIRCULAR ⬇️⬇️⬇️
# from commands import (
#     setup_start_command, 
#     setup_admin_commands, 
#     setup_callbacks, 
#     setup_gen_command,
#     setup_stripe_auth_command,
#     setup_mass_check_command,
#     setup_vbv_command,
#     setup_braintree_ccn_command
# )
# ⬆️⬆️⬆️ FIN DE LA ELIMINACIÓN ⬆️⬆️⬆️

def setup_start_command(bot):
    @bot.message_handler(commands=['start'])
    def start(message):
        try:
            user_id = message.from_user.id
            username = message.from_user.first_name
            credits = get_credits(user_id)
            plan = get_plan(user_id, credits)

            # Agregar información de usos diarios para Free Users
            can_use, remaining = can_use_free_command(user_id)
            if not is_premium(user_id):
                usage_info = f"\n<b>Free Uses Today</b> ∞ {remaining}/30"  # ← Cambiado a 30
            else:
                usage_info = f"\n<b>Free Uses Today</b> ∞ ∞"

            print(f"🔹 Comando /start recibido de {username} - Plan: {plan}")

            photo_url = "https://i.imgur.com/GpFdyRQ.jpeg"
            
            caption = f"""
<b>Plan</b> ∞ {plan}
<b>User Id</b> ∞ <code>{user_id}</code>
<b>Credits</b> ∞ {credits}
{usage_info}

Requested By ∞ {username} [{plan}]
"""

            keyboard = types.InlineKeyboardMarkup()
            
            # Solo mostrar botones básicos para Free Users
            keyboard.add(
                types.InlineKeyboardButton("GATES", callback_data="gates"),
                types.InlineKeyboardButton("TOOLS", callback_data="tools")
            )
            
            # Solo Owner ve Self Shop
            if user_id == ADMIN_ID:
                keyboard.add(types.InlineKeyboardButton("Self Shop", callback_data="shop"))
            
            keyboard.add(types.InlineKeyboardButton("CLOSE", callback_data="close"))

            bot.send_photo(message.chat.id, photo_url, caption=caption, 
                          reply_markup=keyboard, parse_mode="HTML")
            
        except Exception as e:
            print(f"🔴 Error en /start: {e}")
            try:
                bot.reply_to(message, f"❌ Error: {str(e)}")
            except:
                pass

    @bot.message_handler(content_types=['new_chat_members'])
    def new_chat_member(message):
        try:
            for new_member in message.new_chat_members:
                if new_member.id == bot.get_me().id:
                    welcome_text = """
🤖 ¡Gracias por agregarme al grupo!

💡 **Comandos disponibles:**
/start - Menú principal
/gen - Generar tarjetas  
/st - Checkear tarjeta (30 usos diarios gratis)
/b3 - Checkear Braintree CCN (30 usos diarios gratis)
/vbv - Verificación 3D Secure (30 usos diarios gratis)
/ms - Mass check (Solo Premium)

🔐 **Nota:** Comandos de checkeo tienen 30 usos diarios para Free Users.
                    """
                    bot.reply_to(message, welcome_text)
        except Exception as e:
            print(f"🔴 Error en new_chat_member: {e}")

    @bot.message_handler(commands=['help'])
    def help_command(message):
        try:
            help_text = """
🆘 **COMANDOS DISPONIBLES**

🔹 **Básicos:**
/start - Menú principal
/help - Esta ayuda

🔹 **Generación:**
/gen bin - Generar tarjetas (Gratis)

🔹 **Checkeo Individual (30 usos diarios gratis):**
/st cc|mm|aa|cvv - Checkear tarjeta Stripe Auth
/vbv cc|mm|aa|cvv - Verificación 3D Secure
/b3 cc|mm|aa|cvv - Checkeo Braintree CCN

🔹 **Mass Check (Solo Premium):**
/ms cc1 cc2 cc3 - Mass check (2 créditos por APPROVED)
"""
            bot.reply_to(message, help_text, parse_mode="Markdown")
        except Exception as e:
            print(f"🔴 Error en /help: {e}")