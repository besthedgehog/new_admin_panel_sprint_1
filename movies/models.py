# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from .mixins import TimeStampedMixin, UUIDMixin


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    # blank=True делает поле необязательным для заполнения.
    description = models.TextField(_('description'), blank=True)


    def __str__(self):
        return self.name

    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = "content\".\"genre"
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

class Filmwork(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    certificate = models.CharField(_('certificate'), max_length=512, blank=True)
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')

    class Type(models.TextChoices):
        movie = ('MOV', 'movie')
        tv_show = ('TV', 'tv_show')

        class Meta:
            verbose_name = _('type')
            verbose_name_plural = _('types')

    type = models.CharField(
        _('type'),
        max_length=50,
        choices=Type.choices,
        default=Type.movie
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"filmwork"
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmworks')
        indexes = [
            models.Index(fields=['created'], name='film_work_creation_date_idx')
        ]
    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)]
    )

    @property
    def title(self):
        return self.name

    @property
    def creation_date(self):
        return self.created

class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        indexes = [
            models.Index(fields=['film_work'], name='genre_film_work_filmwork_idx'),
            models.Index(fields=['genre'], name='genre_film_work_genre_idx'),
            # Индекс для двух полей film_work и genre
            models.Index(fields=['film_work', 'genre'], name='genre_film_work_fw_genre_idx'),
        ]
        constraints = [
            # Уникальное ограничение для сочетания film_work и genre
            models.UniqueConstraint(fields=['film_work', 'genre'], name='unique_film_genre')
        ]


class Person(models.Model):

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")

    name = models.CharField(_('name'), max_length=255)

    def __str__(self):
        return self.name

class PersonFilmwork(UUIDMixin):
    class Role(models.TextChoices):
        DIRECTOR = 'DIR', _('Director')
        ACTOR = 'ACT', _('Actor')
        PRODUCER = 'PROD', _('Producer')
        WRITER = 'WRIT', _('Writer')
        CINEMATOGRAPHER = 'CINE', _('Cinematographer')
        EDITOR = 'EDIT', _('Editor')
        OTHER = 'OTH', _('Other')

    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.CharField(_('role'), max_length=20, choices=Role.choices, default=Role.OTHER)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        indexes = [
            models.Index(fields=['film_work', 'person', 'role'], name='film_work_person_role_idx')
        ]