import uuid
from dataclasses import dataclass, field
from datetime import datetime


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
