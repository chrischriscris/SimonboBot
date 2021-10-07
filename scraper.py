"""
Bot para obtener material de GecoUsb.

Author: https://github.com/chrischriscris

Este programa está publicado bajo la licencia
GPL-3.0-only.
"""

import requests, sqlite3
from bs4 import BeautifulSoup
from pprint import pprint

def get_and_append_material(URL: str, seccion: str, materia_id: str):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    materiales = soup.find(class_='seccion-list').find_all('a')

    con = sqlite3.connect('lasimonbot.db')
    cur = con.cursor()

    cur.execute(
        'SELECT id FROM secciones WHERE materia_id = ? AND nombre = ?',
        (materia_id, seccion)
    )

    seccion_id = int(cur.fetchone()[0])

    for material in materiales:
        # TODO
        cur.execute(
            'INSERT into material (nombre, seccion_id, url) VALUES (?, ?, ?)', 
            (material.text, seccion_id, material['href'])
        )

    con.commit()
    print("Proceso exitoso.")

def get_and_append_secciones(URL: str, just_return=False):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    secciones = soup.find(class_='materia-list').find_all('a')

    materia_id = soup.find(class_='entry-title').text
    materia_id = materia_id[materia_id.find("(")+1:materia_id.find(")")].replace('-','')

    lista_urls = []

    
    con = sqlite3.connect('lasimonbot.db')
    cur = con.cursor()

    for seccion in secciones:
        ss = seccion.text
        nombre = ss[:ss.find("(")].strip()

        if not just_return:
            cur.execute(
                'INSERT into secciones (nombre, materia_id) VALUES (?, ?)', 
                (nombre, materia_id)
            )
        
        lista_urls.append({
                "seccion": nombre, 
                "materia_id": materia_id,
                "url": seccion["href"]
            }
        )
    
    if not just_return:
        con.commit()
        print("Proceso exitoso.")

    return lista_urls

def get_and_append_materias(URL: str, carrera_id: str):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    materias = soup.find(class_='entry-content').find_all('a')

    con = sqlite3.connect('lasimonbot.db')
    cur = con.cursor()

    for materia in materias:
        mm = materia.text

        nombre = mm[:mm.find("(")].strip()
        codigo = mm[mm.find("(")+1:mm.find(")")].replace('-','')

        cur.execute(
            'INSERT OR IGNORE into materias (codigo, nombre) VALUES (?, ?)', 
            (codigo, nombre)
        )

        # Modificar años
        cur.execute(
            'INSERT OR IGNORE into materias_carrera (carrera_id, materia_id, año) VALUES (?, ?, ?)', 
            (carrera_id, codigo, 1)
        )

    con.commit()
    print("Proceso exitoso.")

def get_materias(URL: str):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    materias = soup.find(class_='entry-content').find_all('a')

    con = sqlite3.connect('lasimonbot.db')
    cur = con.cursor()

    mat_list = []

    for materia in materias:
        mm = materia.text

        nombre = mm[:mm.find("(")].strip()
        codigo = mm[mm.find("(")+1:mm.find(")")].replace('-','')
        url = materia["href"]

        mat_list.append({
                "nombre": nombre,
                "codigo": codigo,
                "url": url
            }
        )

    print("Proceso exitoso.")
    return mat_list

def add_all_material_from_url(URL: str):
    for el in get_and_append_secciones(URL, True):
        get_and_append_material(el['url'], el['seccion'], el['materia_id'])
    print('Proceso exitoso.')

def add_all_secciones(URL: str):
    for el in get_and_append_secciones(URL):
        get_and_append_material(el['url'], el['seccion'], el['materia_id'])
    print('Proceso exitoso.')

def add_all_materias(URL: str):
    con = sqlite3.connect('lasimonbot.db')
    cur = con.cursor()

    for el in get_materias(URL):
        cur.execute(
            'SELECT EXISTS (SELECT id FROM secciones WHERE materia_id = ?)',
            (el["codigo"],)
        )
        exists = cur.fetchone()[0]
        if not exists:
            add_all_secciones(el["url"])

def do_the_thing(URL: str, carrera_id: int):
    get_and_append_materias(URL, carrera_id)
    add_all_materias(URL)