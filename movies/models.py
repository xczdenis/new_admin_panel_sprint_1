from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _

from movies.mixins import TimeStampedMixin, UUIDMixin


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'content"."person'
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilworkTypes(models.TextChoices):
        MOVIE = 'movie', 'movie'
        TV_SHOW = 'tv_show', 'tv_show'

    class AdvancedManager(models.QuerySet):
        def prefetch_genre(self):
            return self.prefetch_related('genres')

        def prefetch_roles(self):
            qs = self.all()
            persons = Person.objects.all()
            maps = {
                'actors': PersonFilmwork.Roles.ACTOR,
                'directors': PersonFilmwork.Roles.DIRECTOR,
                'writers': PersonFilmwork.Roles.WRITER,
            }
            for to_attr, role in maps.items():
                qs = qs.prefetch_related(Prefetch('persons',
                                                  persons.filter(personfilmworks__role=role).distinct(),
                                                  to_attr=to_attr)
                                         )
            return qs

    objects = AdvancedManager.as_manager()
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateTimeField(_('creation_date'), blank=True, null=True)
    rating = models.FloatField(_('rating'), default=0, blank=True, validators=[MinValueValidator(0.0),
                                                                               MaxValueValidator(10.0)])
    type = models.CharField(_('type'), max_length=10, choices=FilworkTypes.choices,
                            default=FilworkTypes.MOVIE)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')
    certificate = models.CharField(_('certificate'), max_length=512, blank=True, null=True, default='')
    file_path = models.FileField(_('file_path'), blank=True, null=True, upload_to='movies/')

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'

    def __str__(self):
        return self.title

    @staticmethod
    def prefetch_roles(queryset):
        queryset = Filmwork.prefetch_actors(queryset)
        queryset = Filmwork.prefetch_directors(queryset)
        queryset = Filmwork.prefetch_writers(queryset)
        return queryset

    @staticmethod
    def prefetch_actors(queryset, **kwargs):
        persons = kwargs.get('persons', Person.objects.all())
        to_attr = kwargs.get('to_attr', 'actors')
        prefetch = Prefetch('persons',
                            persons.filter(personfilmworks__role=PersonFilmwork.Roles.ACTOR).distinct(),
                            to_attr=to_attr)
        return queryset.prefetch_related(prefetch)

    @staticmethod
    def prefetch_directors(queryset, **kwargs):
        persons = kwargs.get('persons', Person.objects.all())
        to_attr = kwargs.get('to_attr', 'directors')
        prefetch = Prefetch('persons',
                            persons.filter(personfilmworks__role=PersonFilmwork.Roles.DIRECTOR).distinct(),
                            to_attr=to_attr)
        return queryset.prefetch_related(prefetch)

    @staticmethod
    def prefetch_writers(queryset, **kwargs):
        persons = kwargs.get('persons', Person.objects.all())
        to_attr = kwargs.get('to_attr', 'writers')
        prefetch = Prefetch('persons',
                            persons.filter(personfilmworks__role=PersonFilmwork.Roles.WRITER).distinct(),
                            to_attr=to_attr)
        return queryset.prefetch_related(prefetch)


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        unique_together = (('film_work', 'genre'),)
        verbose_name = 'Жанр фильма'
        verbose_name_plural = 'Жанры фильма'
        indexes = (models.Index(fields=('film_work', 'genre'), name='film_work_genre_idx'),)


class PersonFilmwork(UUIDMixin):
    class Roles(models.TextChoices):
        DIRECTOR = 'director', 'director'
        WRITER = 'writer', 'writer'
        ACTOR = 'actor', 'actor'

    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE, related_name='personfilmworks')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='personfilmworks')
    role = models.CharField('role', max_length=10, choices=Roles.choices, default=Roles.ACTOR, blank=True,
                            null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        unique_together = (('film_work', 'person'),)
