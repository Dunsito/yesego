# commands/admin.py
from utils.database import get_credits, set_credits, set_premium, is_premium, get_premium_info
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
            if len(parts) != 4:
                bot.reply_to(message, "⚠️ Uso: `/setpremium <user_id> <días> <on/off>`\nEjemplo: `/setpremium 123456789 30 on`\nEjemplo: `/setpremium 123456789 0 off`", parse_mode="Markdown")
                return
                
            user_id = int(parts[1])
            days = int(parts[2])
            premium_status = parts[3].lower()
            
            if premium_status == "on":
                set_premium(user_id, days)
                if days == 0:
                    bot.reply_to(message, f"✅ Usuario {user_id} ahora es Premium Permanente.")
                else:
                    bot.reply_to(message, f"✅ Usuario {user_id} ahora es Premium por {days} días.")
            elif premium_status == "off":
                set_premium(user_id, 0)  # Esto lo removerá inmediatamente
                bot.reply_to(message, f"✅ Usuario {user_id} ahora es Free User.")
            else:
                bot.reply_to(message, "❌ Valor inválido. Usa 'on' o 'off'.")
                
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
                bot.reply_to(message, "⚠️ Uso: `/userinfo <user_id>`", parse_mode="Markdown")
                return
                
            user_id = int(parts[1])
            credits = get_credits(user_id)
            premium_info = get_premium_info(user_id)
            
            if premium_info['is_premium']:
                if premium_info['days_left'] == "∞":
                    plan = "💎 Premium Permanente"
                else:
                    plan = f"💎 Premium ({premium_info['days_left']} días restantes)"
            else:
                plan = "🧊 Free User"
            
            info_text = f"""
👤 **Información del Usuario**

🆔 **ID:** `{user_id}`
💎 **Plan:** {plan}
💰 **Créditos:** {credits}
📅 **Expira:** {premium_info['expire_date']}
🔓 **Premium:** {premium_info['is_premium']}
            """
            
            bot.reply_to(message, info_text, parse_mode="Markdown")
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")