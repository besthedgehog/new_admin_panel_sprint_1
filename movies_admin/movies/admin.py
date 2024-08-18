from django.contrib import admin
from .models import Genre, GenreFilmwork
from .models import Filmwork
from .models import Person


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline,)
    list_display = ('name', 'type', 'created', 'rating',)
    search_fields = ('name', 'description', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass