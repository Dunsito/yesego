# utils/database.py
import json
import os
import datetime
from datetime import timedelta
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
        # Verificar si el premium no ha expirado
        expire_str = user_data.get("premium_expire")
        if expire_str:
            try:
                expire_date = datetime.datetime.strptime(expire_str, "%Y-%m-%d %H:%M:%S")
                if datetime.datetime.now() < expire_date:
                    days_left = (expire_date - datetime.datetime.now()).days
                    return f"💎 Premium ({days_left}d)"
                else:
                    # Premium expirado
                    user_data["premium"] = False
                    user_data.pop("premium_expire", None)
                    save_data(data)
                    return "🧊 Free User"
            except:
                return "💎 Premium"
        return "💎 Premium"
    else:
        return "🧊 Free User"

def set_premium(user_id, days):
    """Establece premium por X días"""
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    
    if days > 0:
        # Calcular fecha de expiración
        expire_date = datetime.datetime.now() + timedelta(days=days)
        data[str(user_id)]["premium"] = True
        data[str(user_id)]["premium_expire"] = expire_date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Remover premium
        data[str(user_id)]["premium"] = False
        data[str(user_id)].pop("premium_expire", None)
    
    save_data(data)

def is_premium(user_id):
    """Verifica si el usuario es premium (incluyendo expiración)"""
    data = load_data()
    user_data = data.get(str(user_id), {})
    
    # Owner siempre es premium
    if user_id == ADMIN_ID:
        return True
    
    # Verificar si tiene premium y no ha expirado
    if user_data.get("premium", False):
        expire_str = user_data.get("premium_expire")
        if expire_str:
            try:
                expire_date = datetime.datetime.strptime(expire_str, "%Y-%m-%d %H:%M:%S")
                if datetime.datetime.now() < expire_date:
                    return True
                else:
                    # Premium expirado - removerlo
                    user_data["premium"] = False
                    user_data.pop("premium_expire", None)
                    save_data(data)
                    return False
            except:
                # Si hay error en la fecha, mantener premium
                return True
        return True
    
    return False

def get_premium_info(user_id):
    """Obtiene información del premium del usuario"""
    data = load_data()
    user_data = data.get(str(user_id), {})
    
    if user_id == ADMIN_ID:
        return {"is_premium": True, "expire_date": "PERMANENTE", "days_left": "∞"}
    
    if user_data.get("premium", False):
        expire_str = user_data.get("premium_expire")
        if expire_str:
            try:
                expire_date = datetime.datetime.strptime(expire_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.datetime.now()
                if now < expire_date:
                    days_left = (expire_date - now).days
                    return {
                        "is_premium": True, 
                        "expire_date": expire_date.strftime("%Y-%m-%d"),
                        "days_left": days_left
                    }
                else:
                    # Premium expirado
                    user_data["premium"] = False
                    user_data.pop("premium_expire", None)
                    save_data(data)
                    return {"is_premium": False, "expire_date": "EXPIRADO", "days_left": 0}
            except:
                return {"is_premium": True, "expire_date": "DESCONOCIDO", "days_left": "?"}
        
        return {"is_premium": True, "expire_date": "PERMANENTE", "days_left": "∞"}
    
    return {"is_premium": False, "expire_date": "NO PREMIUM", "days_left": 0}

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
    remaining = max(0, 30 - daily_usage)
    
    return remaining > 0, remaining