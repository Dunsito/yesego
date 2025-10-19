# utils/bin_database.py - Agrega el campo 'level' a cada BIN
BIN_DATABASE = {
    "434559": {
        "scheme": "VISA",
        "type": "DEBIT", 
        "brand": "CLASSIC",
        "bank": "BANCO DEL ESTADO DE CHILE",
        "country": "CHILE",
        "emoji": "🇨🇱",
        "level": "DEBIT"  # ← Agregar este campo
    },
    "511591": {
        "scheme": "MASTERCARD",
        "type": "CREDIT",
        "brand": "STANDARD",
        "bank": "BANCO SANTANDER",
        "country": "CHILE", 
        "emoji": "🇨🇱",
        "level": "CREDIT"  # ← Agregar este campo
    },
    # ... los demás BINs también necesitan el campo 'level'
}

def get_bin_info(bin_number):
    """
    Obtiene información del BIN desde la base de datos
    """
    # Tomar solo los primeros 6 dígitos
    bin_key = bin_number[:6]
    
    if bin_key in BIN_DATABASE:
        return BIN_DATABASE[bin_key]
    else:
        # Retornar información por defecto si no se encuentra el BIN
        return {
            "scheme": "UNKNOWN",
            "type": "UNKNOWN", 
            "brand": "UNKNOWN",
            "bank": "UNKNOWN BANK",
            "country": "UNKNOWN",
            "emoji": "🏳️",
            "level": "UNKNOWN"  # ← Agregar por defecto también
        }