from models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork

TABLE_GENRE = 'genre'
TABLE_PERSON = 'person'
TABLE_FILMWORK = 'film_work'
TABLE_GENRE_FILMWORK = 'genre_film_work'
TABLE_PERSON_FILMWORK = 'person_film_work'

PG_SCHEME = 'content'

SQL_DB = 'db.sqlite'

TABLES_MAPPING = {
    TABLE_GENRE: Genre,
    TABLE_PERSON: Person,
    TABLE_FILMWORK: Filmwork,
    TABLE_GENRE_FILMWORK: GenreFilmwork,
    TABLE_PERSON_FILMWORK: PersonFilmwork
}
