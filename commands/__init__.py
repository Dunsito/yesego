from .start import setup_start_command
from .admin import setup_admin_commands
from .callback_handler import setup_callbacks
from .gen import setup_gen_command
from .stripe_auth import setup_stripe_auth_command
from .mass_check import setup_mass_check_command
from .vbv_checker import setup_vbv_command
from .braintree_ccn import setup_braintree_ccn_command
from .paypal_charge import setup_paypal_charge_command
from .shop.sites_manager import setup_sites_commands
from .shop.remove_sites import setup_remove_sites_command
from .shop.mass_sh_check import setup_mass_sh_check_command  # ← NUEVO

__all__ = [
    'setup_start_command', 
    'setup_admin_commands', 
    'setup_callbacks', 
    'setup_gen_command',
    'setup_stripe_auth_command',
    'setup_mass_check_command',
    'setup_vbv_command',
    'setup_braintree_ccn_command',
    'setup_paypal_charge_command',
    'setup_sites_commands',
    'setup_remove_sites_command',
    'setup_mass_sh_check_command'  # ← NUEVO
]