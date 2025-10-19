# commands/callback_handler.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import telebot
from telebot import types

def setup_callbacks(bot):
    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        if call.data == "gates":
            show_gates_menu(bot, call)
        elif call.data == "tools":
            show_tools_menu(bot, call)
        elif call.data == "shop":
            bot.answer_callback_query(call.id, "🛒 Self Shop not available yet.")
        elif call.data == "close":
            bot.delete_message(call.message.chat.id, call.message.message_id)
        elif call.data == "back_main":
            back_to_main(bot, call)
        elif call.data == "tool_gen":
            bot.answer_callback_query(call.id, "🔄 Usa: /gen bin")
        elif call.data == "section_auth":
            show_auth_section(bot, call)
        elif call.data == "section_ccn":
            show_ccn_section(bot, call)
        elif call.data == "section_chargeds":
            show_chargeds_section(bot, call)
        elif call.data == "gate_stripe_auth":
            handle_stripe_auth(bot, call)
        elif call.data == "gate_braintree_ccn":
            handle_braintree_ccn(bot, call)
        elif call.data == "gate_paypal_charge":
            handle_paypal_charge(bot, call)
        elif call.data == "coming_soon":
            bot.answer_callback_query(call.id, "🔒 Próximamente...")
        elif call.data == "stripe_process":
            bot.answer_callback_query(call.id, "🔄 Procesar tarjeta - Próximamente")
        elif call.data == "stripe_stats":
            bot.answer_callback_query(call.id, "📊 Stats - Próximamente")

def show_auth_section(bot, call):
    auth_text = """
🔐 **SECCIÓN AUTH**

**Comando:** `/st cc|mm|aa|cvv`
**Función:** Checkeo individual Stripe Auth
**Status:** On ✅  
**Tipo:** Free (30 usos diarios)

**Comando:** `/ms lista_tarjetas`
**Función:** Mass check de tarjetas
**Status:** On ✅
**Tipo:** Premium + Créditos

**Comando:** `/vbv cc|mm|aa|cvv`
**Función:** Verificación de 3D Secure
**Status:** On ✅
**Tipo:** Free (30 usos diarios)

**Ejemplos:**
`/st 4104886655308541|09|29|094`
`/vbv 4673628288456227|01|28|925`
`/ms 4104886655308541|09|29|094 4673628288456227|01|28|925`
"""
    
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=auth_text,
            parse_mode="Markdown",
            reply_markup=create_auth_keyboard()
        )
        bot.answer_callback_query(call.id, "🔐 Sección Auth")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al cargar Auth")

def show_ccn_section(bot, call):
    ccn_text = """
💳 **SECCIÓN CCN**

**Comando:** `/b3 cc|mm|aa|cvv`
**Función:** Checkeo Braintree CCN
**Status:** On ✅  
**Tipo:** Free (30 usos diarios)

**Gateway:** Braintree
**Proxy:** Live ✅

**Ejemplo:**
`/b3 4104886655308541|09|29|094`
"""
    
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=ccn_text,
            parse_mode="Markdown",
            reply_markup=create_ccn_keyboard()
        )
        bot.answer_callback_query(call.id, "💳 Sección CCN")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al cargar CCN")

def show_chargeds_section(bot, call):
    chargeds_text = """
⚡ **SECCIÓN CHARGEDS**

**Comando:** `/pp cc|mm|aa|cvv`
**Función:** PayPal 1$ Charge
**Status:** On ✅  
**Tipo:** Solo Premium (Sin límite)

**Gateway:** PayPal
**Amount:** 1.00 USD

**Ejemplo:**
`/pp 4104886655308541|09|29|094`
"""
    
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=chargeds_text,
            parse_mode="Markdown",
            reply_markup=create_chargeds_keyboard()
        )
        bot.answer_callback_query(call.id, "⚡ Sección Chargeds")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al cargar Chargeds")

def show_gates_menu(bot, call):
    # Configuración de gates
    total_gates = 3  # AUTH, CCN, CHARGEDS
    gates_on = 3     # Todos activos
    gates_off = 0    # Ninguno inactivo
    tools_count = 1  # Solo Gen por ahora
    
    gates_text = f"""
━━━━━「 Gateways 」━━━━━

Total ➝ {total_gates + tools_count}

Gate On > {gates_on} ✅
Gate Off > {gates_off} ❌

Tools > {tools_count} ✅

━━━━━「 Dun bot 」━━━━━
"""
    
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=gates_text,
            parse_mode="Markdown",
            reply_markup=create_gates_main_keyboard()
        )
        bot.answer_callback_query(call.id, "🚪 Menú de Gateways")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al cargar gateways")

def create_gates_main_keyboard():
    """Teclado principal de gates con 3 secciones"""
    keyboard = types.InlineKeyboardMarkup()
    
    # Tres secciones principales
    keyboard.add(
        types.InlineKeyboardButton("🔐 AUTH", callback_data="section_auth"),
        types.InlineKeyboardButton("💳 CCN", callback_data="section_ccn")
    )
    keyboard.add(
        types.InlineKeyboardButton("⚡ CHARGEDS", callback_data="section_chargeds")
    )
    keyboard.add(types.InlineKeyboardButton("⬅️ Back", callback_data="back_main"))
    
    return keyboard

def create_auth_keyboard():
    """Teclado para la sección AUTH"""
    keyboard = types.InlineKeyboardMarkup()
    
    # Botones para cada comando AUTH
    keyboard.add(types.InlineKeyboardButton("🔄 Stripe Auth", callback_data="gate_stripe_auth"))
    keyboard.add(types.InlineKeyboardButton("🔐 VBV Check", callback_data="coming_soon"))
    keyboard.add(types.InlineKeyboardButton("📊 Mass Check", callback_data="coming_soon"))
    keyboard.add(types.InlineKeyboardButton("⬅️ Volver a Gates", callback_data="gates"))
    
    return keyboard

def create_ccn_keyboard():
    """Teclado para la sección CCN"""
    keyboard = types.InlineKeyboardMarkup()
    
    # Botón para Braintree CCN
    keyboard.add(types.InlineKeyboardButton("🔷 Braintree CCN", callback_data="gate_braintree_ccn"))
    keyboard.add(types.InlineKeyboardButton("⬅️ Volver a Gates", callback_data="gates"))
    
    return keyboard

def create_chargeds_keyboard():
    """Teclado para la sección CHARGEDS"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔵 PayPal 1$ Charge", callback_data="gate_paypal_charge"))
    keyboard.add(types.InlineKeyboardButton("⬅️ Volver a Gates", callback_data="gates"))
    return keyboard

def handle_stripe_auth(bot, call):
    """Maneja la selección de Stripe Auth"""
    stripe_auth_text = """
🔐 **Stripe Auth Gateway**

💳 **Comando:** `/st cc|mm|aa|cvv`
🔄 **Función:** Checkeo individual
✅ **Status:** On ✅
🆓 **Tipo:** Free (30 usos diarios)

📝 **Ejemplo:** `/st 4345591122334455|06|29|344`
"""
    
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=stripe_auth_text,
            parse_mode="Markdown",
            reply_markup=create_stripe_auth_keyboard()
        )
        bot.answer_callback_query(call.id, "🔐 Stripe Auth")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al cargar Stripe Auth")

def handle_braintree_ccn(bot, call):
    """Maneja la selección de Braintree CCN"""
    braintree_text = """
💳 **Braintree CCN Gateway**

🔷 **Comando:** `/b3 cc|mm|aa|cvv`
🔄 **Función:** Checkeo Braintree CCN
✅ **Status:** On ✅
🆓 **Tipo:** Free (30 usos diarios)

📝 **Ejemplo:** `/b3 4104886655308541|09|29|094`
"""
    
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=braintree_text,
            parse_mode="Markdown",
            reply_markup=create_braintree_keyboard()
        )
        bot.answer_callback_query(call.id, "💳 Braintree CCN")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al cargar Braintree")

def handle_paypal_charge(bot, call):
    """Maneja la selección de PayPal Charge"""
    paypal_text = """
🔵 **PayPal 1$ Charge**

💸 **Comando:** `/pp cc|mm|aa|cvv`
🔄 **Función:** PayPal 1$ Charge Test
✅ **Status:** On ✅
💎 **Tipo:** Solo Premium (Sin límite)
💵 **Amount:** 1.00 USD

📝 **Ejemplo:** `/pp 4104886655308541|09|29|094`
"""
    
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=paypal_text,
            parse_mode="Markdown",
            reply_markup=create_paypal_keyboard()
        )
        bot.answer_callback_query(call.id, "🔵 PayPal Charge")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al cargar PayPal")

def create_stripe_auth_keyboard():
    """Crea el teclado para Stripe Auth"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("⬅️ Volver a AUTH", callback_data="section_auth"))
    return keyboard

def create_braintree_keyboard():
    """Crea el teclado para Braintree CCN"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("⬅️ Volver a CCN", callback_data="section_ccn"))
    return keyboard

def create_paypal_keyboard():
    """Crea el teclado para PayPal Charge"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("⬅️ Volver a CHARGEDS", callback_data="section_chargeds"))
    return keyboard

def show_tools_menu(bot, call):
    tools_text = """
🛠️ **HERRAMIENTAS DISPONIBLES**

**Name:** Gen
**Use** ↭ `/gen bin`
**Status** ↭ On ✅

**Name:** Checker
**Use** ↭ `/chk cc|mm|yy|cvv`
**Status** ↭ Off ❌

💡 *Selecciona una herramienta o usa los comandos directamente*
"""
    
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=tools_text,
            parse_mode="Markdown",
            reply_markup=create_tools_keyboard()
        )
        bot.answer_callback_query(call.id, "🛠️ Menú de herramientas")
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al cargar herramientas")

def create_tools_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🔄 Gen", callback_data="tool_gen"),
        types.InlineKeyboardButton("🔍 Checker", callback_data="tool_chk")
    )
    keyboard.add(types.InlineKeyboardButton("⬅️ Back", callback_data="back_main"))
    return keyboard

def back_to_main(bot, call):
    from utils.database import get_credits, get_plan
    
    user_id = call.from_user.id
    username = call.from_user.first_name
    credits = get_credits(user_id)
    plan = get_plan(user_id, credits)

    caption = f"""
<b>Plan</b> ∞ {plan}
<b>User Id</b> ∞ <code>{user_id}</code>
<b>Credits</b> ∞ {credits}

Requested By ∞ {username} [{plan}]
"""
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("GATES", callback_data="gates"),
        types.InlineKeyboardButton("TOOLS", callback_data="tools"),
        types.InlineKeyboardButton("Self Shop", callback_data="shop")
    )
    keyboard.add(types.InlineKeyboardButton("CLOSE", callback_data="close"))

    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Error al volver al menú principal")