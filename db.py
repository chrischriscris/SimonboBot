"""
Bot para obtener material de GecoUsb.

Author: https://github.com/chrischriscris

Este programa está publicado bajo la licencia
GPL-3.0-only.
"""

import sqlite3
from constants import DATABASE

def convertir_formato_materia(string: str) -> str:
    '''
    Si la string:
      - Es de longitud 6.
      - Sus primeros dos caracteres son alfabéticos.
      - Los restantes son nuḿéricos.
    Retorna la string en formato de materia (AA-XXXX).
    De otra forma, retorna la misma string.
    '''
    if len(string) != 6:
        return string

    if string[:2].isalpha():
        if string[2:].isnumeric():
            return f'{string[:2]}-{string[2:]}'
    return string

class SimonBotDb:
    database = DATABASE

    # ----------- QUERIES ---------------

    def execute_query(self, sql: str, params: tuple = ()) -> [{}]:
        '''
        Ejecuta una búsqueda en la base de datos. Retorna una lista
        de diccionarios, donde cada elemento corresponde a una fila,
        y las claves de los diccionarios el nombre de la columna.
        '''
        with sqlite3.connect(self.database) as conn:
            conn.row_factory = sqlite3.Row 
            c = conn.cursor()

            c.execute(sql, params)
            fetch = c.fetchall()

            return [dict(row) for row in fetch]

    def execute_query_fetch_one(self, sql: str, params: tuple = ()):
        '''
        Ejecuta una búsqueda en la base de datos. Retorna un único 
        elemento encontrado.
        '''
        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            c.execute(sql, params)
            
            return c.fetchone()

    def select_table(self, table_name: str):
        '''
        Retorna la tabla indicada en table_name como una lista de
        diccionarios, donde cada entrada es una fila.
        '''
        return self.execute_query('SELECT * from ?', (table_name,))

    def get_name_carrera(self, codigo: int) -> str:
        '''
        Retorna el nombre de la carrera cuyo código es el indicado
        en el parámetro.
        '''
        return self.execute_query_fetch_one('SELECT nombre FROM carreras WHERE codigo = ?', (codigo, ))[0]

    def años_carrera(self, codigo: int) -> [(int, str)]:
        '''
        Retorna los años de la carrera cuyo código es el indiicado con
        material disponible en SimonBotDb().
        '''
        años = []

        for i in range(1,6):
            exists = self.execute_query_fetch_one(
                'SELECT EXISTS (SELECT año FROM materias_carrera WHERE año = ? AND carrera_id = ?)',
                (i,codigo)
            )[0]

            if exists:
                if i == 1:
                    años.append((i, 'Primer año'))
                elif i == 2:
                    años.append((i, 'Segundo año'))
                elif i == 3:
                    años.append((i, 'Tercer año'))
                elif i == 4:
                    años.append((i, 'Cuarto año'))
                else:
                    años.append((i, 'Quinto año'))
        return años

    def get_details_seccion(self, id_: int) -> tuple:
        '''
        Recibe un entero con la id de una sección de la base de datos y
        retorna una tripleta con el nombre de la sección, el código y
        el nombre de su materia asociada.
        '''
        seccion, codigo = self.execute_query_fetch_one('SELECT nombre, materia_id FROM secciones WHERE id = ?', (id_,))
        materia = self.execute_query_fetch_one('SELECT nombre FROM materias WHERE codigo = ?', (codigo,))[0]

        return (seccion, codigo, materia)

    def get_details_material(self, id_: int) -> tuple:
        '''
        Recibe un entero con la id de un material de la base de datos y
        retorna una tupla con el nombre del materia y su url.
        '''
        return self.execute_query_fetch_one('SELECT nombre, url FROM material WHERE id = ?', (id_,))

    def fetch_material_from_msg(self, msg: str) -> [{}]:
        '''
        Retorna una lista de diccionarios con el material en la base de
        datos similar al mensaje msg.

        Cada diccionario contiene las claves 'nombre', 'url', 'seccion_id' e 'id'.
        '''
        sql_query = 'SELECT nombre, url, seccion_id, id FROM material WHERE '
        params = [f'%{convertir_formato_materia(word)}%' for word in msg.split(' ')]

        sql_query += 'nombre LIKE ? AND ' * (len(params) - 1) + 'nombre LIKE ?;'
        
        return self.execute_query(sql_query, params)

    def fetch_materias_from_año_carrera(self, año: int, carrera: int) -> [()]:
        '''
        Retorna una lista de tuplas de la forma (codigo, nombre), con el código
        y nombre de las materias en el año dado de la carrera.
        '''
        fetch = self.execute_query(
            '''
            SELECT nombre, codigo FROM materias WHERE codigo IN (
                SELECT materia_id FROM materias_carrera WHERE año = ? AND carrera_id = ?
            );
            ''', (año, carrera))

        return [(el['codigo'], el['nombre']) for el in fetch]

    def fetch_secciones_from_materia(self, codigo: int):
        '''
        Retorna una lista de tuplas de la forma (nombre, id), con el nombre
        y la id de las secciones de la materia con el codigo indicado.
        '''
        fetch = self.execute_query('SELECT nombre, id FROM secciones WHERE materia_id = ?', (codigo,))

        return [(el['nombre'], el['id']) for el in fetch]

    def fetch_material_from_sec_id(self, id_: int):
        '''
        Retorna una lista de diccionarios con el material en la base de
        datos cuya id de sección sea la indicada.

        Cada diccionario contiene las claves 'nombre', 'url', 'seccion_id' e 'id'.
        '''
        return self.execute_query('SELECT nombre, url, seccion_id, id FROM material WHERE seccion_id = ?', (id_, ))

    def get_stats(self) -> (int, int):
        '''
        Devuelve una tupla con el número de usuarios que han usado el
        comando /start y la cantidad de descargas hechas con el bot.
        '''

        downloads = self.execute_query_fetch_one('SELECT SUM(count) FROM descargas')[0]
        users = self.execute_query_fetch_one('SELECT COUNT(id) FROM users')[0]

        return (users, downloads)


    # ---------- ADDITIONS ---------------

    def execute_update(self, sql: str, params: tuple) -> [{}]:
        '''
        Ejecuta una adición/actualización en la base de datos.
        '''
        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            c.execute(sql, params)
            conn.commit()

    def handle_user(self, user: str, id_: int, name: str):
        '''
        Incluye en la base de datos a un nuevo usuario, si no
        existe.
        '''
        self.execute_update('INSERT OR IGNORE INTO users (id, username, name) VALUES (?, ?, ?)', (id_, user, name))

    def handle_download(self, id_: int, increment: int):
        '''
        Actualiza en la base de datos el número de descargas del usuario
        con la id indicada.
        '''
        self.execute_update(
            '''
            INSERT INTO descargas (user_id, count) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET count=count+? 
            ''',
            (id_, increment, increment)
        )