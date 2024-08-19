import sqlite3
from dataclasses import make_dataclass
from dataclasses import dataclass

import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.rows import dict_row

from icecream import ic
import sys


@dataclass
class Table:
    name: str
    sql_creation_command: str

# Словарь для сопоставления типов данных SQLite с типами Python
sqlite_to_python_types = {
    "INTEGER": int,
    "TEXT": str,
    "REAL": float,
    "BLOB": bytes,
    "NUMERIC": float
}


def get_all_information_from_sql(conn):
    '''
    Функция возвращает список SQL запросов
    для создания всех таблиц
    '''

    # В этой переменной хранится список экземпляров 
    # класса Table
    all_tables: list = list()

    # Получаем список всех таблиц в базе данных
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
    info_about_tables = cursor.fetchall()

    for table in info_about_tables:
        all_tables.append(Table(table[1], table[4]))  

    # кортеж с названиями всех таблиц
    names_of_tables: tuple = tuple(i.name for i in all_tables)
    print(names_of_tables)

    # экземпляр класса в списке всех экземпляров
    for table_instance in all_tables:

        table_instance.sql_creation_command = (
            table_instance.sql_creation_command
                .replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
        )

        # получим все данные
        cursor.execute(f"SELECT * FROM {table_instance.name};")
        all_data = list()

        # Извлечём данные по частям 
        n: int = 100 
        while True:
            piece_of_data: tuple = cursor.fetchmany(n)
            if not piece_of_data:
                break
            else:
                all_data.append(piece_of_data)
            
        table_instance.all_data = all_data

        cursor.execute(f"PRAGMA index_list({table_instance.name});")

        indexes = cursor.fetchall()
        for index in indexes:

            # Название индекса
            index_name = index[1]

            # Если индекс уникальный
            if index[2] == 1:

                # Получим все колонки, в которых встречается этот индекс
                cursor.execute(f"PRAGMA index_info({index_name});") # [(0, 0, 'id')]
                index_info = cursor.fetchall()
                columns = tuple(col[2] for col in index_info)

                if len(columns) > 1:
                    unique_index = ',\n    UNIQUE (' + ', '.join(columns) + ')\n)'
                    table_instance.sql_creation_command = (
                        table_instance.sql_creation_command[:-2] + unique_index
                    )


        sqlite_command = f'PRAGMA table_info({table_instance.name});'
        cursor.execute(sqlite_command)
        table_instance.name_of_columns = (
            tuple(i[1] for i in cursor.fetchall())
        )

        print(table_instance.name_of_columns)
        sys.exit()









def divide_list(lst: list, n: int):
    '''
    Генератор, который делит большой список
    на небольшие
    '''
    for i in range(len(lst)//n+1):
        yield tuple(lst[i*n:i*n+n])

def main():
    dsl = {
        'dbname': 'movies_database',
        'user': 'app',
        'password': '123qwe',
        'host': '127.0.0.1',
        'port': 5432
    }

    batch_size = 10 # Количество записей, которое будет выгружаться за один раз

    # Подключение к базам данных
    with (sqlite3.connect('db.sqlite') as sqlite_conn, psycopg.connect(
        **dsl, row_factory=dict_row, cursor_factory=ClientCursor
    ) as pg_conn):
        # get_unique_indexes(sqlite_conn)
        get_all_information_from_sql(sqlite_conn)






if __name__ == '__main__':
    main()

