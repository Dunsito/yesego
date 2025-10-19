# utils/database.py
import json
import os
import datetime
from config import DATA_FILE, ADMIN_ID

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_credits(user_id):
    data = load_data()
    return data.get(str(user_id), {}).get("credits", 0)

def set_credits(user_id, amount):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)]["credits"] = amount
    save_data(data)

def get_plan(user_id, credits):
    data = load_data()
    user_data = data.get(str(user_id), {})
    
    if user_id == ADMIN_ID:
        return "👑 Owner"
    elif user_data.get("premium", False):
        return "💎 Premium User"
    else:
        return "🧊 Free User"

def set_premium(user_id, is_premium):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)]["premium"] = is_premium
    save_data(data)

def is_premium(user_id):
    data = load_data()
    user_data = data.get(str(user_id), {})
    return user_data.get("premium", False) or user_id == ADMIN_ID

def get_daily_usage(user_id):
    """Obtiene el uso diario del usuario"""
    data = load_data()
    user_data = data.get(str(user_id), {})
    usage_data = user_data.get("daily_usage", {})
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Si es un día diferente, reiniciar contador
    if usage_data.get("date") != today:
        return 0
    
    return usage_data.get("count", 0)

def increment_daily_usage(user_id):
    """Incrementa el contador de uso diario"""
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Inicializar daily_usage si no existe
    if "daily_usage" not in data[str(user_id)]:
        data[str(user_id)]["daily_usage"] = {"date": today, "count": 0}
    
    usage_data = data[str(user_id)]["daily_usage"]
    
    # Si es un día diferente, reiniciar contador
    if usage_data.get("date") != today:
        usage_data["date"] = today
        usage_data["count"] = 0
    
    # Incrementar contador
    usage_data["count"] += 1
    save_data(data)
    
    return usage_data["count"]

def can_use_free_command(user_id):
    """Verifica si el usuario puede usar comandos gratis hoy"""
    # Premium users y Owner no tienen límites
    if is_premium(user_id):
        return True, "∞"
    
    daily_usage = get_daily_usage(user_id)
    remaining = max(0, 30 - daily_usage)  # ← CAMBIADO de 50 a 30
    
    return remaining > 0, remaining