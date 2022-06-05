import sqlite3
from dataclasses import dataclass, field

from models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_values
from settings import (PG_SCHEME, TABLE_FILMWORK, TABLE_GENRE, TABLE_GENRE_FILMWORK, TABLE_PERSON,
                      TABLE_PERSON_FILMWORK)


@dataclass
class SQLiteLoader:
    connection: sqlite3.Connection
    batch_size: int = field(default=1000)

    def __post_init__(self):
        self.connection.row_factory = sqlite3.Row

    def fetchmany(self, table: str):
        cur = self.__get_cursor()
        cur.execute('SELECT * FROM {table}'.format(table=table))
        while True:
            batch = cur.fetchmany(self.batch_size)
            if not batch:
                break
            yield batch

    def __get_cursor(self):
        return self.connection.cursor()


@dataclass
class PostgresSaver:
    connection: _connection
    page_size: int = field(default=1000)
    pg_scheme: str = field(default=PG_SCHEME)

    def save_data(self, table, data):
        worker = self.__get_worker(table)
        if worker:
            worker(data)

    @staticmethod
    def __get_fields(model):
        return ','.join(model.__dataclass_fields__.keys())

    @staticmethod
    def __get_values_in_key_order(data_row, keys):
        _data = {}
        for k in keys:
            _data[k] = data_row[k]
        return tuple(_data.values())

    @staticmethod
    def __prepare_data(data, model):
        prepare_data = []
        model_fields = model.__dataclass_fields__.keys()
        for row in data:
            prepare_data.append(PostgresSaver.__get_values_in_key_order(row, model_fields))
        return prepare_data

    def __save_genres(self, data: list[Genre]):
        prepare_data = PostgresSaver.__prepare_data(data, Genre)
        query = self.__get_query(TABLE_GENRE, Genre, 'ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name')
        self.__execute_query(query, prepare_data)

    def __save_persons(self, data: list[Person]):
        prepare_data = PostgresSaver.__prepare_data(data, Person)
        query = self.__get_query(TABLE_PERSON, Person,
                                 'ON CONFLICT (id) DO UPDATE SET full_name=EXCLUDED.full_name')
        self.__execute_query(query, prepare_data)

    def __save_film_work(self, data: list[Filmwork]):
        prepare_data = PostgresSaver.__prepare_data(data, Filmwork)
        query = self.__get_query(TABLE_FILMWORK, Filmwork,
                                 'ON CONFLICT (id) DO UPDATE SET title=EXCLUDED.title')
        self.__execute_query(query, prepare_data)

    def __save_genre_film_work(self, data: list[GenreFilmwork]):
        prepare_data = PostgresSaver.__prepare_data(data, GenreFilmwork)
        query = self.__get_query(TABLE_GENRE_FILMWORK, GenreFilmwork)
        self.__execute_query(query, prepare_data)

    def __save_person_film_work(self, data: list[PersonFilmwork]):
        prepare_data = PostgresSaver.__prepare_data(data, PersonFilmwork)
        query = self.__get_query(TABLE_PERSON_FILMWORK, PersonFilmwork)
        self.__execute_query(query, prepare_data)

    def __get_cursor(self):
        return self.connection.cursor()

    def __get_worker(self, table: str):
        if table == TABLE_GENRE:
            return self.__save_genres
        elif table == TABLE_PERSON:
            return self.__save_persons
        elif table == TABLE_FILMWORK:
            return self.__save_film_work
        elif table == TABLE_PERSON_FILMWORK:
            return self.__save_person_film_work
        elif table == TABLE_GENRE_FILMWORK:
            return self.__save_genre_film_work
        return None

    def __execute_query(self, query, data):
        cur = self.__get_cursor()
        execute_values(cur, query, data, page_size=self.page_size)

    def __get_query(self, table, model, options='ON CONFLICT (id) DO NOTHING'):
        fields = PostgresSaver.__get_fields(model)
        query = 'INSERT INTO {scheme}.{table} ({fields}) values %s {options}'.format(scheme=self.pg_scheme,
                                                                                     table=table,
                                                                                     fields=fields,
                                                                                     options=options)
        return query
