import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

load_dotenv()


@dataclass
class Genre:
    name: str
    created_at: datetime
    updated_at: datetime
    description: str = field(default='')
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    full_name: str
    created_at: datetime
    updated_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Filmwork:
    creation_date: datetime
    created_at: datetime
    updated_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = field(default='')
    description: str = field(default='')
    file_path: str = field(default='')
    rating: float = field(default=0.0)
    type: str = field(default='')

    def __post_init__(self):
        self.certificate = ''


@dataclass
class GenreFilmwork:
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmwork:
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    created_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    role: str = field(default='')


@dataclass
class SQLiteLoader:
    connection: sqlite3.Connection

    def load_genres(self):
        data = self.__load_data('genre')
        return [Genre(**dict(item)) for item in data]

    def load_persons(self):
        data = self.__load_data('person')
        return [Person(**dict(item)) for item in data]

    def load_film_work(self):
        data = self.__load_data('film_work')
        return [Filmwork(**dict(item)) for item in data]

    def load_genre_film_work(self):
        data = self.__load_data('genre_film_work')
        return [GenreFilmwork(**dict(item)) for item in data]

    def load_person_film_work(self):
        data = self.__load_data('person_film_work')
        return [PersonFilmwork(**dict(item)) for item in data]

    def __load_data(self, table_name: str):
        self.connection.row_factory = sqlite3.Row
        curs = self.connection.cursor()
        curs.execute('SELECT * FROM {table_name};'.format(table_name=table_name))
        data = curs.fetchall()
        return data


@dataclass
class PostgresSaver:
    connection: _connection

    def save_genres(self, data: list[Genre]):
        self.__save_data(data, 'genre', 'ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name')

    def save_persons(self, data: list[Person]):
        self.__save_data(data, 'person', 'ON CONFLICT (id) DO UPDATE SET full_name=EXCLUDED.full_name')

    def save_film_work(self, data: list[Filmwork]):
        self.__save_data(data, 'film_work', 'ON CONFLICT (id) DO UPDATE SET title=EXCLUDED.title')

    def save_genre_film_work(self, data: list[GenreFilmwork]):
        self.__save_data(data, 'genre_film_work', 'ON CONFLICT (id) DO NOTHING')

    def save_person_film_work(self, data: list[PersonFilmwork]):
        self.__save_data(data, 'person_film_work', 'ON CONFLICT (id) DO NOTHING')

    @staticmethod
    def __get_fields(instance):
        result = ''
        for k in instance.__dict__.keys():
            result += f'{k}, '
        return result[:-2]

    @staticmethod
    def __get_values(instance):
        result = ''
        for k in instance.__dict__.keys():
            result += f'%({k})s, '
        return result[:-2]

    def __get_query(self, table_name, instance, options):
        fields = PostgresSaver.__get_fields(instance)
        values = PostgresSaver.__get_values(instance)
        query = 'INSERT INTO content.{table} ({fields}) VALUES ({values}) {options};'.format(table=table_name,
                                                                                             fields=fields,
                                                                                             values=values,
                                                                                             options=options)
        curs = self.connection.cursor()
        query = curs.mogrify(query, instance.__dict__).decode('utf-8')
        return query

    def __execute_query(self, query):
        curs = self.connection.cursor()
        curs.execute(query)

    def __save_data(self, data, table, options='ON CONFLICT (id) DO NOTHING'):
        for item in data:
            query = self.__get_query(table, item, options)
            self.__execute_query(query)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    postgres_saver.save_genres(sqlite_loader.load_genres())
    postgres_saver.save_persons(sqlite_loader.load_persons())
    postgres_saver.save_film_work(sqlite_loader.load_film_work())
    postgres_saver.save_genre_film_work(sqlite_loader.load_genre_film_work())
    postgres_saver.save_person_film_work(sqlite_loader.load_person_film_work())


if __name__ == '__main__':
    dsl = {'dbname': os.getenv('DB_NAME'),
           'user': os.getenv('DB_USER'),
           'password': os.getenv('DB_PASSWORD'),
           'host': os.getenv('DB_HOST', '127.0.0.1'),
           'port': os.getenv('DB_PORT', 5432)}
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl,
                                                                       cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
