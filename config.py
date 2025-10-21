# config.py

TOKEN = "8242713813:AAFz44CjKJ1CrZz0WEiLEz4QyeQJomFHNVY"
ADMIN_ID = 6703434014
DATA_FILE = "data.json"

# LISTA CENTRALIZADA DE PROXIES
PROXY_LIST = [
    "p.webshare.io:80:uiwaxqol-rotate:ky0ncy8jz6lo",
    "p.webshare.io:80:lhymcqfk-rotate:c40t0wn62pga", 
    "p.webshare.io:80:nioiisow-rotate:izgswpak25dh",
    "zxo.run.place:6969:dunsito:dunsito",
    "p.webshare.io:80:bhiyynnu-rotate:hq37ts3k50kz",
    "p.webshare.io:80:cegikqjl-rotate:8h4r5i2f0wvx",
    "p.webshare.io:80:dfhjkmnp-rotate:3t9u6y1q7z2w"
]

# MULTI-ENDPOINTS PARA BRAINTREE CCN
BRAINTREE_ENDPOINTS = [
    {
        "name": "Braintree 1",
        "url": "https://componential-unstruggling-shantel.ngrok-free.dev/check_cc?cc={cc}|{mm}|{aa}|{cvv}&email=wasdark336@gmail.com&password=bbmEZs65p!BJLNz"
    }

]

import random

def get_random_proxy():
    """Retorna un proxy aleatorio de la lista"""
    return random.choice(PROXY_LIST)

def get_random_braintree_endpoint():
    """Retorna un endpoint aleatorio de Braintree"""
    return random.choice(BRAINTREE_ENDPOINTS)