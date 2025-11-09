# config.py

TOKEN = "8242713813:AAFz44CjKJ1CrZz0WEiLEz4QyeQJomFHNVY"
ADMIN_ID = 6703434014
DATA_FILE = "data.json"

# LISTA CENTRALIZADA DE PROXIES PARA TODOS LOS COMANDOS
PROXY_LIST = [
    "p.webshare.io:80:uiwaxqol-rotate:ky0ncy8jz6lo",
    "p.webshare.io:80:lhymcqfk-rotate:c40t0wn62pga", 
    "p.webshare.io:80:nioiisow-rotate:izgswpak25dh",
    "zxo.run.place:6969:dunsito:dunsito",
    "p.webshare.io:80:bhiyynnu-rotate:hq37ts3k50kz",
    "p.webshare.io:80:cegikqjl-rotate:8h4r5i2f0wvx",
    "p.webshare.io:80:dfhjkmnp-rotate:3t9u6y1q7z2w"
]

import random

def get_random_proxy():
    """Retorna un proxy aleatorio de la lista"""
    return random.choice(PROXY_LIST)