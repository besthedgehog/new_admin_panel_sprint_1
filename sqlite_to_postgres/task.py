import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from dataclasses import dataclass
from contextlib import contextmanager

# Константы
BATCH_SIZE = 100  # Размер пакета для пакетной загрузки данных

@dataclass
class Film:
    id: int
    title: str
    description: str

@dataclass
class Person:
    id: str  # Учитывая, что id в SQLite текстовый
    name: str

@dataclass
class Genre:
    id: int
    name: str

# Менеджеры контекста для подключения к базам данных
@contextmanager
def sqlite_connection(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def postgres_connection(dbname, user, password, host, port):
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    try:
        yield conn
    finally:
        conn.close()

# Функция для очистки PostgreSQL таблиц
def clear_postgres_tables(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE content.film_work, content.person, content.genre RESTART IDENTITY CASCADE;")
        conn.commit()

# Функции для вставки данных в PostgreSQL
def insert_films(conn, films):
    with conn.cursor() as cur:
        query = """
        INSERT INTO content.film_work (id, title, description, type) 
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, description = EXCLUDED.description, type = EXCLUDED.type;
        """
        execute_values(cur, query, [(f.id, f.title, f.description, 'tv_show') for f in films])  # Устанавливаем значение по умолчанию
        conn.commit()

def insert_persons(conn, persons):
    with conn.cursor() as cur:
        query = """
        INSERT INTO content.person (id, full_name) 
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name;
        """
        execute_values(cur, query, [(p.id, p.name) for p in persons])
        conn.commit()

def insert_genres(conn, genres):
    with conn.cursor() as cur:
        query = """
        INSERT INTO content.genre (id, name) 
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
        """
        execute_values(cur, query, [(g.id, g.name) for g in genres])
        conn.commit()

# Функции для чтения данных из SQLite
def read_films(sqlite_conn):
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id, title, description FROM film_work;")  # Обновляем имя таблицы
    rows = cursor.fetchall()
    return [Film(id=row[0], title=row[1], description=row[2]) for row in rows]

def read_persons(sqlite_conn):
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id, full_name FROM person;")  # Обновляем имя столбца
    rows = cursor.fetchall()
    return [Person(id=row[0], name=row[1]) for row in rows]

def read_genres(sqlite_conn):
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id, name FROM genre;")  # Обновляем имя таблицы
    rows = cursor.fetchall()
    return [Genre(id=row[0], name=row[1]) for row in rows]

# Основная функция
def main():
    sqlite_db_path = 'db.sqlite'

    postgres_db_config = {
        'dbname': 'movies_database',  # Имя базы данных
        'user': 'app',  # Имя пользователя
        'password': '123qwe',  # Пароль
        'host': '127.0.0.1',  # Адрес хоста
        'port': 5432  # Порт
    }

    with sqlite_connection(sqlite_db_path) as sqlite_conn, \
            postgres_connection(**postgres_db_config) as postgres_conn:

        # Очистка таблиц PostgreSQL
        clear_postgres_tables(postgres_conn)

        # Чтение и запись фильмов
        films = read_films(sqlite_conn)
        for i in range(0, len(films), BATCH_SIZE):
            insert_films(postgres_conn, films[i:i + BATCH_SIZE])

        # Чтение и запись персон
        persons = read_persons(sqlite_conn)
        for i in range(0, len(persons), BATCH_SIZE):
            insert_persons(postgres_conn, persons[i:i + BATCH_SIZE])

        # Чтение и запись жанров
        genres = read_genres(sqlite_conn)
        for i in range(0, len(genres), BATCH_SIZE):
            insert_genres(postgres_conn, genres[i:i + BATCH_SIZE])

if __name__ == "__main__":
    main()
