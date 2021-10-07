"""
Bot to get material from GecoUsb.

Author: https://github.com/chrischriscris
"""

import os
import logging
from constants import TOKEN
from handlers import *
from telegram import Update
from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    InlineQueryHandler,
    CallbackContext,
    Filters,
)

def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(token=TOKEN, arbitrary_callback_data=True)
    dp = updater.dispatcher

    # Enable logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logger = logging.getLogger(__name__)

    handler_list = [
        CommandHandler('start', start),
        CommandHandler('buscar', buscar),
        CommandHandler('estadisticas', get_stats),
        MessageHandler(Filters.text & (~Filters.command), buscar_material),
        CallbackQueryHandler(get_material, pattern=lambda x: x[0] == 'obtener material'),
        CallbackQueryHandler(mover_material, pattern=lambda x: x[0] == 'mover material'),
        CallbackQueryHandler(cancelar_busqueda, pattern=lambda x: x[0] == 'cancelar'),
        CallbackQueryHandler(obtener_años_carrera, pattern=lambda x: x[0] == 'obtener carrera'),
        CallbackQueryHandler(mover_carreras, pattern=lambda x: x[0] == 'mover carreras'),
        CallbackQueryHandler(obtener_materias_año, pattern=lambda x: x[0] == 'obtener materias año'),
        CallbackQueryHandler(obtener_secciones, pattern=lambda x: x[0] == 'obtener secciones'),
        CallbackQueryHandler(obtener_material_av, pattern=lambda x: x[0] == 'obtener material av'),
        CallbackQueryHandler(get_all, pattern=lambda x: x[0] == 'descargar todo'),
        InlineQueryHandler(busqueda_inline),
        MessageHandler(Filters.command, unknown),
    ]

    for handler in handler_list:
        dp.add_handler(handler)

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()