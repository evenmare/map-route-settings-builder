import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from ckeditor import fields

from route_settings_builder import validators, querysets


def validate_value(value_type: str, value: str) -> str:
    """
    Валидация значения критерия маршрута
    :param value_type: тип значения
    :param value: значение
    :return: значение
    """
    error_details = {'code': 'invalid', 'params': {'value': value}}

    if (value_type == 'numeric' and
            not (value[1:] if len(value) > 1 and value[0] == '-' else value).replace('.', '', 1).isdigit()):
        raise ValidationError('Значение должно быть числом', **error_details)
    if value_type == 'boolean' and value not in ('0', '1', 'true', 'false'):
        raise ValidationError('Значение должно быть логическим значением: 0, 1, true, false', **error_details)

    return value


class UpdateDescriptionMixin(models.Model):
    """ Информация о времени редактировании и создании модели """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        abstract = True


class Criterion(UpdateDescriptionMixin, models.Model):
    """ Критерий """
    name = models.CharField(max_length=255,
                            null=False,
                            blank=False,
                            db_index=True,
                            verbose_name='Наименование')

    internal_name = models.CharField(max_length=63,
                                     null=False,
                                     blank=False,
                                     unique=True,
                                     db_index=True,
                                     verbose_name='Внутреннее наименование')

    value_type = models.CharField(max_length=7,
                                  null=False,
                                  blank=False,
                                  default='string',
                                  choices=[
                                      ('string', 'Строковый'),
                                      ('numeric', 'Числовой'),
                                      ('boolean', 'Логический'),
                                  ],
                                  verbose_name='Тип значения')

    class Meta:
        verbose_name = 'Критерий'
        verbose_name_plural = 'критерии'

    def __str__(self) -> str:
        return f'{self.name}'


class Place(UpdateDescriptionMixin, models.Model):
    """ Место """
    name = models.CharField(max_length=255,
                            null=False,
                            blank=False,
                            db_index=True,
                            verbose_name='Наименование')

    description = fields.RichTextField(null=True,
                                       blank=True,
                                       verbose_name='Описание')

    latitude = models.DecimalField(max_digits=8,
                                   decimal_places=6,
                                   null=False,
                                   blank=False,
                                   validators=[validators.validate_latitude],
                                   verbose_name='Широта')

    longitude = models.DecimalField(max_digits=9,
                                    decimal_places=6,
                                    null=False,
                                    blank=False,
                                    validators=[validators.validate_longitude],
                                    verbose_name='Долгота')

    criteria = models.ManyToManyField(Criterion,
                                      through='PlaceCriterion',
                                      related_name='places',
                                      verbose_name='Критерии')

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'места'

    def __str__(self) -> str:
        return f'{self.name}'


class PlaceCriterion(models.Model):
    """ Критерий для места """
    place = models.ForeignKey(Place,
                              on_delete=models.CASCADE,
                              verbose_name='Место')

    criterion = models.ForeignKey(Criterion,
                                  on_delete=models.PROTECT,
                                  verbose_name='Критерий')

    value = models.CharField(max_length=255,
                             null=False,
                             blank=True,
                             verbose_name='Значение')

    def clean(self):
        super().clean()
        validate_value(self.criterion.value_type, self.value)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['place', 'criterion']
        verbose_name = 'Критерий для места'
        verbose_name_plural = 'критерии для места'

    def __str__(self) -> str:
        return f'{self.criterion.internal_name}'


class Route(UpdateDescriptionMixin, models.Model):
    """ Маршрут """
    uuid = models.UUIDField(default=uuid.uuid4,
                            unique=True,
                            editable=False,
                            db_index=True,
                            verbose_name='Идентификатор')

    name = models.CharField(max_length=255,
                            null=False,
                            blank=False,
                            db_index=True,
                            verbose_name='Наименование')

    details = models.JSONField(null=True,
                               blank=True,
                               verbose_name='Детализация маршрута')

    places = models.ManyToManyField(Place,
                                    through='RoutePlace',
                                    related_name='routes',
                                    verbose_name='Места')

    criteria = models.ManyToManyField(Criterion,
                                      through='RouteCriterion',
                                      related_name='routes',
                                      verbose_name='Критерии')

    guide_description = fields.RichTextField(null=True,
                                             blank=True,
                                             verbose_name='Описание путеводителя')

    guide_image = models.ImageField(upload_to='guides/',
                                    null=True,
                                    blank=True,
                                    verbose_name='Файл путеводителя')

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True,
                               on_delete=models.SET_NULL,
                               related_name='routes',
                               verbose_name='Автор')

    objects = querysets.RouteQuerySet.as_manager()

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'маршруты'

    def __str__(self) -> str:
        return self.name


class RouteCriterion(models.Model):
    """ Критерий для маршрута """
    route = models.ForeignKey(Route,
                              on_delete=models.CASCADE,
                              verbose_name='Маршрут')

    criterion = models.ForeignKey(Criterion,
                                  on_delete=models.PROTECT,
                                  verbose_name='Критерий')

    value = models.CharField(max_length=255,
                             null=False,
                             blank=True,
                             verbose_name='Значение')

    def clean(self):
        super().clean()
        validate_value(self.criterion.value_type, self.value)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['route', 'criterion']
        verbose_name = 'Критерий для маршрута'
        verbose_name_plural = 'критерии для маршрута'

    def __str__(self) -> str:
        return self.criterion.internal_name


class RoutePlace(models.Model):
    """ Место маршрута """
    route = models.ForeignKey(Route,
                              on_delete=models.CASCADE,
                              verbose_name='Маршрут')

    place = models.ForeignKey(Place,
                              on_delete=models.PROTECT,
                              verbose_name='Место')

    class Meta:
        unique_together = ['route', 'place']
        verbose_name = 'Место маршрута'
        verbose_name_plural = 'места маршрута'
