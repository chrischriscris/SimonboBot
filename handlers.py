"""
Bot para obtener material de GecoUsb.

Author: https://github.com/chrischriscris

Este programa está publicado bajo la licencia
GPL-3.0-only.
"""

from telegram import Update, InlineQueryResultDocument, Document
from telegram.ext import CallbackContext
from db import SimonBotDb
from keyboards import *
from constants import CARRERAS

# ---------- ADMIN COMMANDS --------------------

def get_stats(update: Update, context: CallbackContext):
    DB = SimonBotDb()
    users, dls = DB.get_stats()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'{users} usuarios han usado el SimonboBot.\n{dls} descargas se han hecho.'
    )

# ---------- INLINE QUERY -----------------

def busqueda_inline(update: Update, context: CallbackContext):
    """Handle the inline query."""
    userTg = update.effective_user
    user = userTg.username
    user_id = userTg.id
    name = f'{userTg.first_name} {userTg.last_name}'
    
    query = update.inline_query.query.strip()

    if query == "":
        return

    DB = SimonBotDb()
    DB.handle_user(user, user_id, name)
    fetch = DB.fetch_material_from_msg(query)

    if len(fetch) > 50:
        fetch = fetch[:50]

    if len(fetch) == 0:
        return
    else:
        results = []
        for result in fetch:
            id_, nombre, url = (
                result['id'],
                result['nombre'],
                result['url']
            )

            results.append(
                InlineQueryResultDocument(
                    id=id_,
                    title=nombre[:-4],
                    caption=f'<b>📃 {nombre[:-4]}</b>',
                    parse_mode='HTML',
                    document_url=f'{url.strip().replace(" ", "%20")}',
                    mime_type='application/pdf'
                )
            )

        update.inline_query.answer(results)


# ---------- BÚSQUEDA DE MATERIAL ----------------

def get_material(update: Update, context: CallbackContext):
    query = update.callback_query
    id_ = query.data[1]

    context.drop_callback_data(query)
    query.answer()

    DB = SimonBotDb()
    material, url = DB.get_details_material(id_)
    query.edit_message_text(text=f'Opción seleccionada: {material}')

    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=url,
        caption=f'<b>📃 {material[:-4]}</b>',
        parse_mode='HTML'
    )

    gracias(update, context)

    userTg = update.effective_user
    user = userTg.username
    user_id = userTg.id
    name = f'{userTg.first_name} {userTg.last_name}'

    DB.handle_user(user, user_id, name)
    DB.handle_download(update.effective_user.id, 1)

def mover_material(update: Update, context: CallbackContext):
    query = update.callback_query
    fetch, begin = query.data[1], query.data[2]

    context.drop_callback_data(query)
    query.answer()

    text, kb_markup = create_keyboard_material(fetch, begin)

    query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=kb_markup
    )

def buscar_material(update: Update, context: CallbackContext):
    DB = SimonBotDb()
    fetch = DB.fetch_material_from_msg(update.message.text.strip())
    
    if len(fetch) != 0:
        text, kb_markup = create_keyboard_material(fetch, 0)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=kb_markup
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='0 resultados encontrados :(. Intenta hacer una búsqueda más clara, ' \
                'usando el código de la materia y/o siguiendo las normas de acentuación.\n\n' \
                'También puedes intentar a usar el comando /buscar y hacer una búsqueda avanzada.'
        )

# ------------ BÚSQUEDA AVANZADA -------------------

def obtener_material_av(update: Update, context: CallbackContext):
    query = update.callback_query
    seccion_id, begin = query.data[1], query.data[2]
    DB = SimonBotDb()

    context.drop_callback_data(query)
    query.answer()
    fetch = DB.fetch_material_from_sec_id(seccion_id)

    text, kb_markup = create_keyboard_material(fetch, begin)

    query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=kb_markup
    )

def obtener_secciones(update: Update, context: CallbackContext):
    query = update.callback_query
    codigo = query.data[1]

    context.drop_callback_data(query)
    query.answer()

    kb_markup = create_keyboard_secciones(codigo)

    query.edit_message_text(
        text='Selecciona la sección:',
        reply_markup=kb_markup
    )

def obtener_materias_año(update: Update, context: CallbackContext):
    query = update.callback_query
    codigo, año = query.data[1], query.data[2]

    context.drop_callback_data(query)
    query.answer()

    kb_markup = create_keyboard_materias(codigo, año)

    query.edit_message_text(
        text='Selecciona una materia:',
        reply_markup=kb_markup
    )

def obtener_años_carrera(update: Update, context: CallbackContext):
    query = update.callback_query
    codigo = query.data[1]

    context.drop_callback_data(query)
    query.answer()

    kb_markup = create_keyboard_años(codigo)

    query.edit_message_text(
        text='Selecciona un año de la carrera:',
        reply_markup=kb_markup
    )

def mover_carreras(update: Update, context: CallbackContext):
    query = update.callback_query
    CARRERAS, begin = query.data[1], query.data[2]

    context.drop_callback_data(query)
    query.answer()

    kb_markup = create_keyboard_carreras(CARRERAS, begin)

    query.edit_message_text(
        text='Selecciona la carrera:',
        reply_markup=kb_markup
    )

def buscar(update: Update, context: CallbackContext):

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Selecciona la carrera:' ,
        reply_markup=create_keyboard_carreras(CARRERAS, 0)
    )

# -------------- HANDLERS GENÉRICOS ---------------------


def start(update: Update, context: CallbackContext):
    DB = SimonBotDb()
    userTg = update.effective_user

    user = userTg.username
    user_id = userTg.id
    name = f'{userTg.first_name} {userTg.last_name}'

    DB.handle_user(user, user_id, name)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f'¡Hola, {userTg.first_name}! Bienvenidos al SimonboBot.')

def get_all(update: Update, context: CallbackContext):
    query = update.callback_query
    fetch = query.data[1]

    context.drop_callback_data(query)
    query.answer()

    DB = SimonBotDb()
    query.edit_message_text(text=f'Opción seleccionada: Descargar todo.')

    for material in fetch:
        material, url = DB.get_details_material(material['id'])
        context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=url,
            caption=f'<b>📃 {material[:-4]}</b>',
            parse_mode='HTML'
        )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='¡Listo!'
    )

    gracias(update, context)

    userTg = update.effective_user
    user = userTg.username
    user_id = userTg.id
    name = f'{userTg.first_name} {userTg.last_name}'

    DB.handle_user(user, user_id, name)
    DB.handle_download(update.effective_user.id, len(fetch))

def cancelar_busqueda(update: Update, context: CallbackContext):
    query = update.callback_query
    context.drop_callback_data(query)
    query.answer()
    query.edit_message_text(
        text='Búsqueda cancelada.'
    )

def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Comando desconocido.')

def gracias(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='📚 Recuerda que todo el material que puedes bajar usando el bot proviene de la página de ' \
            '<a href="https://gecousb.com.ve/">GECO USB</a>, y está disponible gracias al esfuerzo y ' \
            'trabajo durante años de los integrantes de la agrupación en recopilar y generar material ' \
            'para la comunidad uesebista.',
        parse_mode='HTML'
    )