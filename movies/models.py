from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


# Определим два миксина
class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        # Этот параметр указывает Django, что этот класс не является представлением таблицы
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField('name', max_length=255)
    # blank=True делает поле необязательным для заполнения.
    description = models.TextField('description', blank=True)


    def __str__(self):
        return self.name

    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = "content\".\"genre"
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class Filmwork(UUIDMixin, TimeStampedMixin):
    name = models.CharField('name', max_length=255)
    description = models.TextField('description', blank=True)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    certificate = models.CharField(_('certificate'), max_length=512, blank=True)
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')

    class Type(models.TextChoices):
        movie = ('MOV', 'movie')
        tv_show = ('TV', 'tv_show')

    type = models.CharField(
        max_length=7,
        choices=Type.choices,
        default=Type.movie
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"filmwork"
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'

    rating = models.FloatField('rating', blank=True,
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



class Person(models.Model):
    pass

class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField('role')
    created = models.DateTimeField(auto_now_add=True)