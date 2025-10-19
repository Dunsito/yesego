# commands/broadcast.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import load_data
from config import ADMIN_ID

def setup_broadcast_command(bot):
    @bot.message_handler(commands=['bc'])
    def broadcast_message(message):
        # Verificar que es el Owner
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "⛔ Comando exclusivo para Owner.")
            return

        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2:
                bot.reply_to(message, "⚠️ Uso: `/bc mensaje`\nEjemplo: `/bc ¡Nuevas funciones disponibles!`", parse_mode="Markdown")
                return
            
            broadcast_text = parts[1]
            
            # Obtener todos los usuarios de la base de datos
            data = load_data()
            user_ids = list(data.keys())
            
            # Enviar mensaje de procesamiento
            processing_msg = bot.reply_to(message, f"📢 Enviando broadcast a {len(user_ids)} usuarios...")
            
            # Contadores
            success_count = 0
            fail_count = 0
            
            # Enviar mensaje a cada usuario
            for user_id in user_ids:
                try:
                    bot.send_message(user_id, f"📢 **ANUNCIO IMPORTANTE**\n\n{broadcast_text}\n\n_Enviado por el equipo del bot_", parse_mode="Markdown")
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    print(f"❌ Error enviando a {user_id}: {str(e)}")
            
            # Resultado final
            result_text = f"""
✅ **Broadcast Completado**

📊 **Estadísticas:**
• ✅ Enviados: {success_count} usuarios
• ❌ Fallidos: {fail_count} usuarios
• 📝 Total: {len(user_ids)} usuarios

💡 _Los usuarios que bloquearon el bot no recibieron el mensaje._
"""
            bot.edit_message_text(result_text, processing_msg.chat.id, processing_msg.message_id)
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error en broadcast: {str(e)}")