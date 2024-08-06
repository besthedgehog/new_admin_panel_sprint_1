import sqlite3
import psycopg
from psycopg import ClientCursor
from psycopg.rows import dict_row
import sys
import os
from datetime import datetime

# Добавим родительскую директорию в sys.path чтобы разрешить абсолютные импорты
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Импортируем уже созданную фнукцию для получения данных из Postgre
from sqlite_to_postgres.migration_from_sqlite_to_postgresql \
import get_all_information_from_sql as get_all_information_from_sqlite


def transform_datetime(dt: datetime) -> str:
    formatted_datetime = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    formatted_timezone = dt.strftime('%z')[:3]  # Take only the first three characters of the timezone

    while formatted_datetime[-1] == '0': # Уберём незначащие нули
        formatted_datetime = formatted_datetime[:-1]

    return f"{formatted_datetime}{formatted_timezone}"


def get_all_information_from_postgre(conn):
    '''
    Функция получает данные из всех интересующих нас таблиц
    '''
    list_with_necessary_tables = [
        'film_work',
        'genre',
        'genre_film_work',
        'person',
        'person_film_work'
    ]

    cursor = conn.cursor()
    cursor.execute('''
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema = 'content'
        ORDER BY table_name;
    ''')
    all_tables = [i['table_name'] for i in cursor.fetchall()]

    assert set(list_with_necessary_tables).issubset(set(all_tables)), 'В PostgreSQL не все таблицы'


    data = dict()

    sql_comamnd = '''
        SELECT * from {};
    '''


    for table in list_with_necessary_tables:

        cursor.execute(sql_comamnd.format(table))

        # Список со словарями
        # Для таблицы genre
        # [{id: ..., name: ..., description: ..., created_at, updated_at: ...}]
        data_from_table = cursor.fetchall() # Вся инормация из одной таблицы

        list_with_data = list()

        # итерируемся по каждому словарю
        for dict_with_data in data_from_table:
            tmp_list = list() # Нужен для приведения к стуркутре как в Postgre
            # приводим формат записи даты к нужному нам
            for element in tuple(dict_with_data.values()):
                if isinstance(element, datetime):
                    tmp_list.append(transform_datetime(element))
                else:
                    tmp_list.append(element)


            list_with_data.append(tuple(tmp_list))


        data[table] = list_with_data


    return data


def check_equality_of_data(data_from_sqlite, data_from_postgres):
    '''
    Функция проверяет равенство данных
    полученных из двух баз данных
    '''

    # Для начала проверим совпадение таблиц
    assert set(data_from_sqlite.keys()) == set(data_from_postgres.keys()), 'Таблицы не совпадают'

    for table in data_from_sqlite.keys():
        data_from_sqlite[table] = data_from_sqlite[table][1]

        # В ходе обработки данных порядок записей мог сбиться, поэтому
        # Нужно сравнивать множества или применять сортировку
        if set(data_from_sqlite[table]) != set(data_from_postgres[table]):
            print(f'Несовпадение в таблице {table}')
            for i in range(len(data_from_sqlite[table])):
                if data_from_sqlite[table][i] != data_from_postgres[table][i]:
                    print(f'sqlite {data_from_sqlite[table][i]}')
                    print()
                    print(f'Postgre {data_from_postgres[table][i]}')
                    return False

    return True


dsl = {
    'dbname': 'movies_database',
    'user': 'app',
    'password': '123qwe',
    'host': '127.0.0.1',
    'port': 5432
}

def main():
    path_to_sqlite_db = '../../sqlite_to_postgres/db.sqlite'
    with (sqlite3.connect(path_to_sqlite_db) as sqlite_conn, psycopg.connect(
        **dsl, row_factory=dict_row, cursor_factory=ClientCursor
    ) as pg_conn):
        data_from_sqlite = get_all_information_from_sqlite(sqlite_conn)

        data_from_postgre = get_all_information_from_postgre(pg_conn)


        print(check_equality_of_data(data_from_sqlite, data_from_postgre))


if __name__ == '__main__':
    main()
