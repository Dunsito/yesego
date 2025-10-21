# utils/bin_database.py - Consulta BINs en tiempo real desde bins.antipublic.cc
import requests
import json
import time

# Cache local para no hacer requests repetidas
BIN_CACHE = {}
CACHE_DURATION = 3600  # 1 hora en segundos

def get_bin_info(bin_number):
    """
    Obtiene información del BIN desde bins.antipublic.cc API
    Extrae los primeros 6 dígitos y busca en la web en tiempo real
    """
    # Tomar solo los primeros 6 dígitos
    bin_key = str(bin_number)[:6]
    
    # Verificar que sea un BIN válido (6 dígitos)
    if len(bin_key) < 6 or not bin_key.isdigit():
        return get_default_bin_info(bin_key)
    
    # Verificar si está en cache y es reciente
    if bin_key in BIN_CACHE:
        cached_data, timestamp = BIN_CACHE[bin_key]
        if time.time() - timestamp < CACHE_DURATION:
            print(f"🔹 [BIN] Cache hit para {bin_key}")
            return cached_data
    
    print(f"🔹 [BIN] Consultando API para {bin_key}")
    
    try:
        # bins.antipublic.cc API
        response = requests.get(
            f"https://bins.antipublic.cc/bins/{bin_key}",
            timeout=10,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔹 [BIN] Respuesta API para {bin_key}: {data}")
            
            # Convertir emoji Unicode a caracteres normales
            country_flag = convert_unicode_emoji(data.get('country_flag', '🏳️'))
            
            # Mapear al formato que necesitamos
            bin_info = {
                "scheme": data.get('brand', 'UNKNOWN'),
                "type": data.get('type', 'UNKNOWN'),
                "brand": data.get('level', 'UNKNOWN'),
                "bank": data.get('bank', 'UNKNOWN BANK'),
                "country": data.get('country_name', 'UNKNOWN'),
                "emoji": country_flag,
                "level": data.get('level', 'UNKNOWN')
            }
            
            # Guardar en cache
            BIN_CACHE[bin_key] = (bin_info, time.time())
            print(f"✅ [BIN] Info obtenida para {bin_key}: {bin_info['bank']} - {bin_info['country']}")
            return bin_info
            
        else:
            print(f"❌ [BIN] API returned status {response.status_code} for BIN {bin_key}")
            
    except requests.exceptions.Timeout:
        print(f"❌ [BIN] Timeout consultando BIN {bin_key}")
    except requests.exceptions.ConnectionError:
        print(f"❌ [BIN] Connection error consultando BIN {bin_key}")
    except requests.exceptions.RequestException as e:
        print(f"❌ [BIN] Request error consultando BIN {bin_key}: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ [BIN] JSON decode error para BIN {bin_key}: {e}")
    except Exception as e:
        print(f"❌ [BIN] Error general consultando BIN {bin_key}: {e}")
    
    # Si falla la API, retornar información por defecto
    print(f"🔹 [BIN] Usando info por defecto para {bin_key}")
    default_info = get_default_bin_info(bin_key)
    BIN_CACHE[bin_key] = (default_info, time.time())
    return default_info

def convert_unicode_emoji(unicode_str):
    """
    Convierte emojis Unicode (como ðŸ‡²ðŸ‡½) a caracteres normales
    """
    try:
        if unicode_str and 'ð' in unicode_str:
            # Los emojis Unicode vienen codificados, los decodificamos
            return unicode_str.encode('latin-1').decode('utf-8')
        return unicode_str
    except:
        return '🏳️'

def get_default_bin_info(bin_number):
    """
    Información por defecto si la API falla
    """
    if not bin_number or len(bin_number) < 1:
        bin_number = '4'
    
    first_digit = bin_number[0] if bin_number else '4'
    
    if first_digit == '4':
        scheme = "VISA"
        brand = "CLASSIC"
        card_type = "DEBIT"
    elif first_digit == '5':
        scheme = "MASTERCARD" 
        brand = "STANDARD"
        card_type = "CREDIT"
    elif first_digit == '3':
        scheme = "AMEX"
        brand = "GOLD"
        card_type = "CREDIT"
    elif first_digit == '6':
        scheme = "DISCOVER"
        brand = "STANDARD"
        card_type = "CREDIT"
    else:
        scheme = "UNKNOWN"
        brand = "UNKNOWN"
        card_type = "UNKNOWN"
    
    return {
        "scheme": scheme,
        "type": card_type, 
        "brand": brand,
        "bank": "UNKNOWN BANK",
        "country": "UNKNOWN",
        "emoji": "🏳️",
        "level": "UNKNOWN"
    }

def clear_bin_cache():
    """Limpia el cache de BINs"""
    global BIN_CACHE
    BIN_CACHE = {}
    print("🔹 [BIN] Cache limpiado")

def get_bin_cache_info():
    """Retorna información del cache (útil para debugging)"""
    return {
        "cache_size": len(BIN_CACHE),
        "cached_bins": list(BIN_CACHE.keys())
    }

# Función de prueba
def test_bin_lookup():
    """Función para probar el sistema con BINs conocidos"""
    test_bins = [
        "547046",  # Santander México
        "512717",  # Capital One USA
        "402318",  # Banorte México
        "450635",  # Por probar
        "544239"   # Por probar
    ]
    
    for bin_test in test_bins:
        print(f"\n🔍 Probando BIN: {bin_test}")
        result = get_bin_info(bin_test)
        print(f"📊 Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
        time.sleep(1)  # Pausa entre requests

if __name__ == "__main__":
    test_bin_lookup()