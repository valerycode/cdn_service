import logging
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from config.components.common import MINIO_MASTER_STORAGE
from .schemas import UploadTask
from .service import upload_file

logger = logging.getLogger(__name__)


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255, unique=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        ordering = ("name",)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(
        _('full name'),
        max_length=255
    )

    class Meta:
        db_table = "content\".\"person"
        ordering = ("full_name",)
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return self.full_name


def set_filename(instance, filename):
    return str(instance.id)


class FilmworkLoadStatusToS3(models.TextChoices):
    WAITING = 'waiting', _('Waiting')
    FAILED = 'failed', _('Failed')
    DONE = 'done', _('Done')


class Filmwork(UUIDMixin, TimeStampedMixin):

    class FilmworkTypes(models.TextChoices):
        MOVIE = 'movie', _('movie'),
        TV_SHOW = 'tv_show', _('tv_show')

    title = models.CharField(
        _('title'),
        max_length=255,
        unique=True
    )
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation date'))
    file = models.FileField(
        _('file'),
        upload_to=set_filename,
    )
    rating = models.FloatField(
        _('rating'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    type = models.CharField(
        _('type'),
        max_length=7,
        choices=FilmworkTypes.choices,
        help_text="Выберите тип произведения"
    )
    status = models.CharField(
        _('Status'),
        max_length=50,
        choices=FilmworkLoadStatusToS3.choices,
        default=FilmworkLoadStatusToS3.WAITING,
    )
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = "content\".\"film_work"
        ordering = ("-creation_date",)
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'genre'],
                name='unique_film_work_genre'
            )]
        verbose_name = 'Жанр фильма'
        verbose_name_plural = 'Жанры фильма'

    def __str__(self):
        return ''


class RoleTypes(models.TextChoices):
    ACTOR = 'actor', _('actor')
    DIRECTOR = 'director', _('director')
    WRITER = 'writer', _('writer')


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(
        _('role'),
        max_length=8,
        choices=RoleTypes.choices,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'person', 'role'],
                name='unique_film_work_person'
            )]
        verbose_name = 'Участник фильма'
        verbose_name_plural = 'Участники фильма'

    def __str__(self):
        return ''


class Storage(UUIDMixin, TimeStampedMixin):
    size = models.PositiveBigIntegerField(
        _('size'),
        help_text=_("Enter the storage size in gigabytes"),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(15360)
        ])
    url = models.CharField(_('url'), max_length=200)
    geo_ip = models.GenericIPAddressField(_('geo_ip'),)

    class Meta:
        db_table = "content\".\"storage"
        ordering = ("-size",)
        verbose_name = 'Хранилище'
        verbose_name_plural = 'Хранилища'

    def __str__(self):
        return self.url


@receiver(pre_save, sender=Storage)
def convert_to_bytes(sender, instance, *args, **kwargs):
    instance.size *= 1024 * 1024 * 1024


@receiver(post_save, sender=Filmwork)
def upload_file_to_master(sender, instance, created, **kwargs):
    if created and instance.file:
        task = UploadTask(
            file_path=instance.file.path,
            object_name=instance.file.name,
            storage=MINIO_MASTER_STORAGE
        )
        upload_file(task)
