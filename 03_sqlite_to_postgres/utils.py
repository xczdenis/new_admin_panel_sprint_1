import sqlite3
from contextlib import contextmanager

from settings import TABLES_MAPPING


def get_model_by_table(table):
    return TABLES_MAPPING.get(table, None)


@contextmanager
def sqlite_conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
