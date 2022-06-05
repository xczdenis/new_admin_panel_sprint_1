from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.mixins import TimeStampedMixin, UUIDMixin


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'content"{0}"genre'.format('.')
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'content"{0}"person'.format('.')
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilworkTypes(models.TextChoices):
        MOVIE = 'movie', 'movie'
        TV_SHOW = 'tv_show', 'tv_show'

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateTimeField(_('creation_date'), blank=True, null=True)
    rating = models.FloatField(_('rating'), default=0, blank=True, validators=[MinValueValidator(0),
                                                                               MaxValueValidator(100)])
    type = models.CharField(_('type'), max_length=10, choices=FilworkTypes.choices, default=FilworkTypes.MOVIE)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')
    certificate = models.CharField(_('certificate'), max_length=512, blank=True, null=True, default='')
    file_path = models.FileField(_('file_path'), blank=True, null=True, upload_to='movies/')

    class Meta:
        db_table = 'content"{0}"film_work'.format('.')
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"{0}"genre_film_work'.format('.')
        unique_together = (('film_work', 'genre'),)
        verbose_name = 'Жанр фильма'
        verbose_name_plural = 'Жанры фильма'
        indexes = (models.Index(fields=('film_work', 'genre'), name='film_work_genre_idx'),)


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.TextField('role', default='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"{0}"person_film_work'.format('.')
        unique_together = (('film_work', 'person'),)
        indexes = (models.Index(fields=('film_work', 'person'), name='film_work_person_idx'),)
