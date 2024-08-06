import sqlite3
from dataclasses import make_dataclass

import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.rows import dict_row

from icecream import ic
import sys

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

    cursor = conn.cursor()

    # Получаем список всех таблиц в базе данных
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    data_from_all_tables = dict()

    # Получим название таблиц и SQL-команды для их создания
    for table in tables:
        data_from_all_tables[table[2]] = [table[-1]]

    unique_indexes = dict()

    for table_name in data_from_all_tables.keys():
        cursor.execute(f"SELECT * FROM {table_name};")
        stroki = cursor.fetchall()
        data_from_all_tables[table_name].append(stroki)

        sql_command = data_from_all_tables[table_name][0]
        if 'CREATE TABLE IF NOT EXISTS' not in sql_command:
            sql_command = sql_command.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
            data_from_all_tables[table_name][0] = sql_command

        cursor.execute(f"PRAGMA index_list({table_name});")  # все индексы, которые есть в таблице
        indexes = cursor.fetchall()
        table_indexes = []
        for index in indexes:
            index_name = index[1]
            if index[2] == 1:  # Проверяем, является ли индекс уникальным
                cursor.execute(f"PRAGMA index_info({index_name});")  # все колонки, в которых встречается этот индекс
                index_info = cursor.fetchall()
                columns = tuple(col[2] for col in index_info)
                if len(columns) > 1:
                    table_indexes.append((index_name, columns))
                    unique_index = ',UNIQUE (' + ', '.join(columns) + ')\n)'
                    data_from_all_tables[table_name][0] = sql_command[:-1] + unique_index


    # Внесем информацию о заголовках таблиц
    for table in data_from_all_tables.keys():
        sqlite_command = f'PRAGMA table_info({table});'
        cursor.execute(sqlite_command)
        data = tuple(i[1] for i in cursor.fetchall())
        data_from_all_tables[table].append(data)



    return data_from_all_tables


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
        tableS = get_all_information_from_sql(sqlite_conn)
        # ic(a.__dict__)

        for tablename in tableS.keys():
            # print(tableS[tablename][0])
            cursor = pg_conn.cursor()
            cursor.execute(f'DROP TABLE {tablename};')
            cursor.execute(tableS[tablename][0]) # Создание таблиц по SQL запросу

            data = tableS[tablename][1]

            # Создадим строку, содержащую имена столбцов таблицы
            # Например id name description created_at updated_at
            names_of_columns: tuple = tableS[tablename][-1]

            string_for_name_of_columns: str = (', '.join(
                ['{}' for _ in range(len(names_of_columns))])
                                               ).format(*names_of_columns)

            string_with_S: str = ', '.join(
                ['%s' for _ in range(len(names_of_columns))]
            )


            sql_command = f'''
            INSERT INTO {tablename} ({string_for_name_of_columns})
            VALUES ({string_with_S})
            '''

            for batch_of_information in divide_list(data, batch_size):
                cursor.executemany(sql_command, batch_of_information)






if __name__ == '__main__':
    main()


# АЛКОритм
# Получить все данных из SQLite (названия таблиц, команды создания таблиц, строки из таблиц, ограничения таблиц (уникальность))
# Создать все таблицы в PostgreSQL c помощью названий и команд
# Создать все ограничения для таблиц в PostgreSQL (массив имён колонок таблицы с уникальными значеними)
# Вставляем данные из SQLite в PostgreSQL
# Сравнение данных в таблицах SQLite с PostgreSQL
