# commands/shop/remove_sites.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import load_data, save_data

def setup_remove_sites_command(bot):
    @bot.message_handler(commands=['rm'])
    def handle_remove_sites(message):
        process_remove_sites(bot, message)

def process_remove_sites(bot, message):
    """Maneja la eliminación de sitios (/rm)"""
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    try:
        parts = message.text.split()
        
        if len(parts) == 1:
            # Mostrar ayuda si no hay parámetros
            show_remove_help(bot, message, user_id)
            return
        
        command = parts[1].lower()
        
        if command == "all":
            # Eliminar todos los sitios
            remove_all_sites(user_id)
            bot.reply_to(message, f"✅ Los sitios han sido eliminados.")
            
        elif command.isdigit():
            # Eliminar un sitio específico por índice
            index = int(command) - 1  # Convertir a índice base 0
            success, site_name = remove_site_by_index(user_id, index)
            
            if success:
                bot.reply_to(message, f"✅ **Sitio eliminado:** `{site_name}`")
            else:
                bot.reply_to(message, f"❌ **Índice inválido.** Usa `/rm` para ver tus sitios disponibles.")
                
        else:
            # Intentar eliminar por nombre del sitio
            site_to_remove = ' '.join(parts[1:])
            success = remove_site_by_name(user_id, site_to_remove)
            
            if success:
                bot.reply_to(message, f"✅ **Sitio eliminado:** `{site_to_remove}`")
            else:
                bot.reply_to(message, f"❌ **Sitio no encontrado:** `{site_to_remove}`\n\nUsa `/rm` para ver tus sitios disponibles.")
                
    except Exception as e:
        bot.reply_to(message, f"❌ Error al eliminar sitios: {str(e)}")

def show_remove_help(bot, message, user_id):
    """Muestra ayuda para el comando /rm"""
    user_sites = get_user_sites(user_id)
    
    if user_sites:
        sites_list = "\n".join([f"`{i+1}.` `{site}`" for i, site in enumerate(user_sites)])
        response = f"""

📋 **Tus sitios actuales:**
{sites_list}

🛠️ **Comandos disponibles:**
`/rm all` - Eliminar todos los sitios
`/rm 1` - Eliminar el sitio número 1
`/rm ejemplo.com` - Eliminar sitio por nombre

💡 **Ejemplos:**
`/rm all` → Elimina todo
`/rm 2` → Elimina el segundo sitio  
`/rm google.com` → Elimina google.com
"""
    else:
        response = """
🗑️ **ELIMINAR SITIOS**

❌ **No tienes sitios configurados.**

 Primero agrega sitios con:
`/site example.com`
`/sites site1.com site2.com`

"""
    
    bot.reply_to(message, response, parse_mode="Markdown")

def get_user_sites(user_id):
    """Obtiene la lista de sitios del usuario"""
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str in data and 'sites' in data[user_id_str]:
        return data[user_id_str]['sites']
    return []

def remove_all_sites(user_id):
    """Elimina todos los sitios del usuario"""
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str in data and 'sites' in data[user_id_str]:
        data[user_id_str]['sites'] = []
        save_data(data)
        return True
    return False

def remove_site_by_index(user_id, index):
    """Elimina un sitio por índice"""
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str in data and 'sites' in data[user_id_str]:
        sites = data[user_id_str]['sites']
        
        if 0 <= index < len(sites):
            removed_site = sites.pop(index)
            data[user_id_str]['sites'] = sites
            save_data(data)
            return True, removed_site
    
    return False, None

def remove_site_by_name(user_id, site_name):
    """Elimina un sitio por nombre"""
    data = load_data()
    user_id_str = str(user_id)
    site_name_lower = site_name.lower()
    
    if user_id_str in data and 'sites' in data[user_id_str]:
        sites = data[user_id_str]['sites']
        
        # Buscar y eliminar el sitio (case insensitive)
        new_sites = [site for site in sites if site.lower() != site_name_lower]
        
        if len(new_sites) < len(sites):  # Si se eliminó algún sitio
            data[user_id_str]['sites'] = new_sites
            save_data(data)
            return True
    
    return False    