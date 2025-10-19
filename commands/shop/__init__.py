# commands/shop/__init__.py
from .sites_manager import setup_sites_commands
from .remove_sites import setup_remove_sites_command
from .mass_sh_check import setup_mass_sh_check_command  # ← CORREGIDO (agregar el punto)

__all__ = ['setup_sites_commands', 'setup_remove_sites_command', 'setup_mass_sh_check_command']