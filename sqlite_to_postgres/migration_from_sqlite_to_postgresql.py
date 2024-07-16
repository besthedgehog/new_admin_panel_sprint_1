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

class Data:
    '''
    В экземплярах класса будет содеражаться вся информация
    о таблицах из базы данных
    '''
    pass


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
        raise Exception('Стоп')
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
# db_path = 'db.sqlite'
# data = fetch_data_as_dataclass(db_path)
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







    return data_from_all_tables



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
        # get_unique_indexes(sqlite_conn)
        tableS = get_all_information_from_sql(sqlite_conn)
        # ic(a.__dict__)

        for tablename in tableS.keys():
            print(tableS[tablename][0])
            cursor = pg_conn.cursor()
            cursor.execute(f'DROP TABLE {tablename};')
            cursor.execute(tableS[tablename][0])


        # with open('log', 'w') as f:
        #     for i in a.stroki:
        #         print(i)
        #         break
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
