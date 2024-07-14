import sqlite3
from dataclasses import make_dataclass

import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.rows import dict_row

from icecream import ic

# Словарь для сопоставления типов данных SQLite с типами Python
sqlite_to_python_types = {
    "INTEGER": int,
    "TEXT": str,
    "REAL": float,
    "BLOB": bytes,
    "NUMERIC": float
}

def create_dataclass_from_table(cursor, table_name: str):
    # Получаем информацию о колонках таблицы
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    # Создаем поля для dataclass
    fields = [(col[1], sqlite_to_python_types.get(col[2].upper(), str)) for col in columns]

    # Создаем dataclass динамически
    return make_dataclass(table_name.capitalize(), fields)

def fetch_data_as_dataclass(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем список всех таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    data = {}

    for table in tables:
        # print(table) ################
        table_name = table[0]  # Извлекаем имя таблицы из кортежа



        # Создаем dataclass для текущей таблицы
        TableDataClass = create_dataclass_from_table(cursor, table_name)

        # Выполняем запрос для получения данных из текущей таблицы
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Преобразуем строки данных в экземпляры dataclass
        data[table_name] = [TableDataClass(*row) for row in rows]

    conn.close()
    return data

# Пример использования
db_path = 'db.sqlite'
data = fetch_data_as_dataclass(db_path)
#
# for table_name, records in data.items():
#     print(f"Table: {table_name}")
#     for record in records:
#         print(record)

def get_all_information_from_sql(conn):
    '''
    Функция возвращает список SQL запросов
    для создания всех таблиц
    '''

    cursor = conn.cursor()

    # Получаем список всех таблиц в базе данных
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    data_from_all_tables = list()

    # Получим название таблиц и SQL-команды для их создания
    for table in tables:
        list_with_data = [table[2], table[-1]]
        print()
        print(list_with_data) ################
        print()
        data_from_all_tables.append(list_with_data)

    # Получим unique индексы
    # cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
    # cursor.execute(f"PRAGMA index_list({table_name});")

    # for name_of_table in

    return data_from_all_tables


def get_unique_indexes(conn):
    # conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем список всех таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    unique_indexes = dict()



    for table_name in tables:
        table_name = table_name[0]  # Извлекаем имя таблицы из кортежа ('genre',)
        cursor.execute(f"PRAGMA index_list({table_name});") # все индексы, которые есть в таблице
        indexes = cursor.fetchall()

        # ic | indexes: [(0, 'film_work_genre', 1, 'c', 0),
        #                (1, 'sqlite_autoindex_genre_film_work_1', 1, 'pk', 0)]


        table_indexes = []
        for index in indexes:
            index_name = index[1] # (0, 'film_work_genre', 1, 'c', 0)
            if index[2] == 1:  # Проверяем, является ли индекс уникальным
                cursor.execute(f"PRAGMA index_info({index_name});") # все колонки, в которых встречается этот индекс
                index_info = cursor.fetchall() # ic| index_info: [(0, 1, 'film_work_id'), (1, 2, 'genre_id')]
                columns = [col[2] for col in index_info]
                table_indexes.append((index_name, columns))

        if table_indexes:
            unique_indexes[table_name] = table_indexes

    # ic(unique_indexes)

    table_of_unique_indexes = dict()

    print(unique_indexes)
    print()


    for table, indexes in unique_indexes.items():
        for index_name, columns in indexes:
            print(*columns)
            if table not in table_of_unique_indexes:
                table_of_unique_indexes[table] = []
            table_of_unique_indexes[table].append({index_name: columns})

    for table, indexes in unique_indexes.items():
        print(f"Table: {table}")
        for index_name, columns in indexes:
            print(f"  Unique Index: {index_name}, Columns: {', '.join(columns)}")
    return table_of_unique_indexes




def main():
    dsl = {
        'dbname': 'movies_database',
        'user': 'app',
        'password': '123qwe',
        'host': '127.0.0.1',
        'port': 5432
    }

    # Подключение к базам данных
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg.connect(
        **dsl, row_factory=dict_row, cursor_factory=ClientCursor
    ) as pg_conn:
        ic(get_unique_indexes(sqlite_conn))
        # get_all_information_from_sql(sqlite_conn)
        # unique_indexes = get_unique_indexes(sqlite_conn)
        # for table, indexes in unique_indexes.items():
        #     print(f"Table: {table}")
        #     for index_name, columns in indexes:
        #         print(f"  Unique Index: {index_name}, Columns: {', '.join(columns)}")

        # Получим все табилцы из PostgreSQL





        # ### Начнём с того, что создадим таблицы в PostgreSQL
        # tables_creation_commands = get_tables_creation_commands(sqlite_conn)
        #
        # for i in tables_creation_commands:
        #     print(i)


if __name__ == '__main__':
    main()


# АЛКОритм
# Получить все данных из SQLite (названия таблиц, команды создания таблиц, строки из таблиц, ограничения таблиц (уникальность))
# Создать все таблицы в PostgreSQL c помощью названий и команд
# Создать все ограничения для таблиц в PostgreSQL (массив имён колонок таблицы с уникальными значеними)
# Вставляем данные из SQLite в PostgreSQL
# Сравнение данных в таблицах SQLite с PostgreSQL
