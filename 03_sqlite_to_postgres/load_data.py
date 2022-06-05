import os
import sqlite3

from dotenv import load_dotenv
from loaders import PostgresSaver, SQLiteLoader
from psycopg2.extensions import connection as _connection
from settings import TABLE_FILMWORK, TABLE_GENRE, TABLE_GENRE_FILMWORK, TABLE_PERSON, TABLE_PERSON_FILMWORK
from utils import get_model_by_table, pg_conn_context, sqlite_conn_context

load_dotenv()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    sqlite_loader = SQLiteLoader(connection)
    postgres_saver = PostgresSaver(pg_conn)
    tables_to_upload = [TABLE_GENRE, TABLE_PERSON, TABLE_FILMWORK, TABLE_GENRE_FILMWORK,
                        TABLE_PERSON_FILMWORK]

    for table in tables_to_upload:
        model = get_model_by_table(table)
        if model:
            for batch in sqlite_loader.fetchmany(table):
                postgres_saver.save_data(table, batch)


if __name__ == '__main__':
    dsn = {'dbname': os.getenv('DB_NAME'),
           'user': os.getenv('DB_USER'),
           'password': os.getenv('DB_PASSWORD'),
           'host': os.getenv('DB_HOST', '127.0.0.1'),
           'port': os.getenv('DB_PORT', 5432)}
    with sqlite_conn_context('db.sqlite') as sqlite_conn, pg_conn_context(dsn) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
