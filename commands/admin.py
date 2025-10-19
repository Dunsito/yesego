# commands/admin.py
from utils.database import get_credits, set_credits, set_premium, is_premium
from config import ADMIN_ID

def setup_admin_commands(bot):
    @bot.message_handler(commands=['addcredits'])
    def add_credits(message):
        # Solo el Owner puede usar este comando
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "⛔ Comando exclusivo para Owner.")
            return

        try:
            parts = message.text.split()
            if len(parts) != 3:
                bot.reply_to(message, "⚠️ Uso correcto: /addcredits <user_id> <cantidad>")
                return
                
            user_id = int(parts[1])
            amount = int(parts[2])

            current = get_credits(user_id)
            set_credits(user_id, current + amount)

            bot.reply_to(message, f"✅ Se añadieron {amount} créditos al usuario {user_id}.")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

    @bot.message_handler(commands=['setpremium'])
    def set_premium_command(message):
        # Solo el Owner puede usar este comando
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "⛔ Comando exclusivo para Owner.")
            return

        try:
            parts = message.text.split()
            if len(parts) != 3:
                bot.reply_to(message, "⚠️ Uso correcto: /setpremium <user_id> <true/false>")
                return
                
            user_id = int(parts[1])
            premium_status = parts[2].lower()
            
            if premium_status == "true":
                set_premium(user_id, True)
                bot.reply_to(message, f"✅ Usuario {user_id} ahora es Premium User.")
            elif premium_status == "false":
                set_premium(user_id, False)
                bot.reply_to(message, f"✅ Usuario {user_id} ahora es Free User.")
            else:
                bot.reply_to(message, "❌ Valor inválido. Usa 'true' o 'false'.")
                
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

    @bot.message_handler(commands=['userinfo'])
    def user_info(message):
        # Solo el Owner puede usar este comando
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "⛔ Comando exclusivo para Owner.")
            return

        try:
            parts = message.text.split()
            if len(parts) != 2:
                bot.reply_to(message, "⚠️ Uso correcto: /userinfo <user_id>")
                return
                
            user_id = int(parts[1])
            credits = get_credits(user_id)
            premium_status = is_premium(user_id)
            plan = "💎 Premium" if premium_status else "🧊 Free"
            
            info_text = f"""
👤 **Información del Usuario**

🆔 **ID:** `{user_id}`
💎 **Plan:** {plan}
💰 **Créditos:** {credits}
🔓 **Premium:** {premium_status}
            """
            
            bot.reply_to(message, info_text, parse_mode="Markdown")
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")