"""
Bot para obtener material de GecoUsb.

Author: https://github.com/chrischriscris

Este programa estΓ‘ publicado bajo la licencia
GPL-3.0-only.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from db import *

class TGKeyboard:
    def __init__(self):
        self.row = []
        self.keyboard = []

    def append_to_row(self, text: str, callback_data: ()):
        self.row.append(InlineKeyboardButton(text, callback_data=callback_data))

    def append_row(self):
        self.keyboard.append(self.row)
        self.row = []

    def reset(self):
        self.row = []
        self.keyboard = []

    def append(self, text: str, callback_data: ()):
        self.append_to_row(text, callback_data)
        self.append_row()

    def get(self):
        return InlineKeyboardMarkup(self.keyboard)

def create_keyboard_material(fetch: list, begin: int) -> (str, InlineKeyboardMarkup):
    '''
    Recibe una lista de diccionarios con los resultados de una query y un indice.

    Retorna un InlineKeyboard con 5 opciones de material para elegir.
    '''
    DB = SimonBotDb()
    kb = TGKeyboard()
    text = f'{len(fetch)} resultados encontrados:\n\n'
    
    if len(fetch) <= begin + 5:
        end = len(fetch)
    else:
        end = begin + 5

    for i in range(begin, end):
        material, id_, seccion_id = (
            fetch[i]['nombre'], 
            int(fetch[i]['id']), 
            int(fetch[i]['seccion_id'])
        )

        seccion, codigo, materia = DB.get_details_seccion(seccion_id)
        
        text += f'π {i + 1}. <b>{material[:-4]}</b> ({material[-3:].upper()})\n' \
            f'π {materia} ({codigo})\n' \
            f'π {seccion}\n\n'

        kb.append_to_row(i + 1, ('obtener material', id_))
            
    kb.append_row()

    if begin != 0: 
        kb.append_to_row('β¬οΈ', ('mover material', fetch, begin - 5))

    kb.append_to_row('β', ('cancelar', 0))

    if end != len(fetch):
        kb.append_to_row('β‘οΈ', ('mover material', fetch, begin + 5))

    kb.append_row()

    kb.append('Descargar todo', ('descargar todo', fetch))

    return (text, kb.get())

def create_keyboard_carreras(CARRERAS: [()], begin: int) -> InlineKeyboardMarkup:
    '''
    Recibe una lista de tuplas de la forma (xxxx, emoji), donde la primera
    entrada es un entero con el cΓ³digo de una carrera, y la segunda su emoji
    correspondiente, y un entero con el indice de la primera carrera a mostrar
    en el teclado.

    Retorna un InlineKeyboard con 8 opciones de carrera para elegir.
    '''
    DB = SimonBotDb()
    kb = TGKeyboard()

    if len(CARRERAS) <= begin + 8:
        end = len(CARRERAS)
    else:
        end = begin + 8

    for i in range(begin, end):
        codigo, emoji = CARRERAS[i]
        nombre = DB.get_name_carrera(codigo)

        if codigo < 1000:
            text=f'0{codigo} - {emoji} {nombre}'
        else:
            text=f'{codigo} - {emoji} {nombre}'

        kb.append(text, ('obtener carrera', codigo))

    if begin != 0: 
        kb.append_to_row('β¬οΈ', ('mover carreras', CARRERAS, begin - 8))

    kb.append_to_row('β', ('cancelar', 0))

    if end != len(CARRERAS):
        kb.append_to_row('β‘οΈ', ('mover carreras', CARRERAS, begin + 8))

    kb.append_row()

    return kb.get()

def create_keyboard_aΓ±os(codigo: int) -> InlineKeyboardMarkup:
    DB = SimonBotDb()
    aΓ±os = DB.aΓ±os_carrera(codigo)
    kb = TGKeyboard()

    for aΓ±o, aΓ±o_text in aΓ±os:
        kb.append(aΓ±o_text, ('obtener materias aΓ±o', codigo, aΓ±o))

    kb.append('β', ('cancelar', 0))

    return kb.get()

def create_keyboard_materias(codigo: int, aΓ±o: int) -> InlineKeyboardMarkup:
    DB = SimonBotDb()
    materias = DB.fetch_materias_from_aΓ±o_carrera(aΓ±o, codigo)
    kb = TGKeyboard()

    for codigo, nombre in materias:
        kb.append(f'({codigo}) {nombre}', ('obtener secciones', codigo))

    kb.append('β', ('cancelar', 0))

    return kb.get()

def create_keyboard_secciones(codigo: str) -> InlineKeyboardMarkup:
    DB = SimonBotDb()
    secciones = DB.fetch_secciones_from_materia(codigo)
    kb = TGKeyboard()

    for nombre, id_ in secciones:
        kb.append(nombre, ('obtener material av', id_, 0))

    kb.append('β', ('cancelar', 0))

    return kb.get()