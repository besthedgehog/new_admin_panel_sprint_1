CREATE TABLE genre (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);
CREATE TABLE genre_film_work (
    id TEXT PRIMARY KEY,
    film_work_id TEXT NOT NULL,
    genre_id TEXT NOT NULL,
    created_at timestamp with time zone
);
CREATE UNIQUE INDEX film_work_genre ON genre_film_work (film_work_id, genre_id);
CREATE TABLE person_film_work (
    id TEXT PRIMARY KEY,
    film_work_id TEXT NOT NULL,
    person_id TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at timestamp with time zone
);
CREATE UNIQUE INDEX film_work_person_role ON person_film_work (film_work_id, person_id, role);
CREATE TABLE IF NOT EXISTS "person"( id text primary key, full_name text not null, created_at timestamp with time zone, updated_at timestamp with time zone);
CREATE TABLE IF NOT EXISTS "film_work" (    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    file_path TEXT,
    rating FLOAT,
    type TEXT not null,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);
