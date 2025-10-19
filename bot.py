import telebot
from config import TOKEN
from commands import (
    setup_start_command, 
    setup_admin_commands, 
    setup_callbacks, 
    setup_gen_command,
    setup_stripe_auth_command,
    setup_mass_check_command,
    setup_vbv_command,
    setup_braintree_ccn_command,
    setup_paypal_charge_command,
    setup_sites_commands,
    setup_remove_sites_command,
    setup_mass_sh_check_command,
    setup_broadcast_command,
    setup_mass_b3_check_command
)

def main():
    bot = telebot.TeleBot(TOKEN)
    
    setup_start_command(bot)
    setup_admin_commands(bot)
    setup_callbacks(bot)
    setup_gen_command(bot)
    setup_stripe_auth_command(bot)
    setup_mass_check_command(bot)
    setup_vbv_command(bot)
    setup_braintree_ccn_command(bot)
    setup_paypal_charge_command(bot)
    setup_sites_commands(bot)
    setup_remove_sites_command(bot)  # ← NUEVA LÍNEA
    setup_mass_sh_check_command(bot)
    setup_broadcast_command(bot)
    setup_mass_b3_check_command(bot)
    
    print("✅ Bot en ejecución... Comandos cargados: /start, /gen, /st, /ms, /vbv, /b3, /pp, /site, /sites, /sh, /rm")
    bot.polling(non_stop=True)

if __name__ == "__main__":
    main()