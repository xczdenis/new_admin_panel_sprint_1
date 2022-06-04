import pytest


@pytest.mark.usefixtures('sqlite_cursor', 'pg_cursor')
class TestConsistency:
    @pytest.mark.parametrize('table', ['film_work', 'genre', 'genre_film_work', 'person', 'person_film_work'])
    def test_row_count(self, sqlite_cursor, pg_cursor, table):
        """The number of rows in SQL table should be equal PG table"""
        sql_count = 'sql'
        pg_count = 'pg'
        sqlite_cursor.execute('SELECT COUNT(id) FROM {table};'.format(table=table))
        result = sqlite_cursor.fetchone()
        sql_count = result[0]

        pg_cursor.execute('SELECT COUNT(id) FROM content.{table};'.format(table=table))
        result = pg_cursor.fetchone()
        pg_count = result[0]

        assert sql_count == pg_count

    @pytest.mark.parametrize('table', ['film_work', 'genre', 'genre_film_work', 'person', 'person_film_work'])
    def test_table_content(self, sqlite_cursor, pg_cursor, table):
        def is_equal(dict1: dict, dict2: dict) -> (bool, str, str, str):
            for k, v in dict1.items():
                if k not in ('certificate', 'created_at', 'updated_at'):
                    if v or dict2[k]:
                        if dict2[k] != v:
                            return False, k, v, dict2[k]
            return True, '', '', ''

        sqlite_cursor.execute('SELECT * FROM {table} ORDER BY id;'.format(table=table))
        data_sql = sqlite_cursor.fetchall()

        pg_cursor.execute('SELECT * FROM content.{table} ORDER BY id;'.format(table=table))
        data_pg = pg_cursor.fetchall()

        result = (True, '', '', '')
        for i in range(len(data_sql)):
            try:
                result = is_equal(dict(data_pg[i]), dict(data_sql[i]))
            except Exception as e:
                result = (False, e, '', '')
            if not result[0]:
                break
        assert result[0], f'key: {result[1]}; pg-value={result[2]}; sql-value={result[3]}'
