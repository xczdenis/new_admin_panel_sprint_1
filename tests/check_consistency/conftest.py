import sqlite3

import psycopg2
import pytest
from psycopg2.extras import DictCursor


@pytest.fixture(scope='session')
def sqlite_cursor():
    connection = sqlite3.connect('03_sqlite_to_postgres/db.sqlite')
    connection.row_factory = sqlite3.Row
    return connection.cursor()


@pytest.fixture(scope='session')
def pg_cursor():
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1',
           'port': 5432}
    connection = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    return connection.cursor()
