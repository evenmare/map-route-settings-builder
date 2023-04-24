from django.db import models
from django.conf import settings

from ckeditor import fields

from route_settings_builder import validators


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
                            verbose_name='Наименование')

    internal_name = models.CharField(max_length=63,
                                     null=False,
                                     blank=False,
                                     unique=True,
                                     verbose_name='Внутреннее наименование')

    value_type = models.CharField(max_length=7,
                                  null=False,
                                  blank=False,
                                  default='string',
                                  choices=[
                                      ('string', 'Строковый'),
                                      ('numeric', 'Числовой'),
                                      ('range', 'Диапазон'),
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
                            verbose_name='Наименование')

    description = fields.RichTextField(null=True,
                                       blank=True,
                                       verbose_name='Описание')

    longitude = models.DecimalField(max_digits=8,
                                    decimal_places=5,
                                    null=False,
                                    blank=False,
                                    validators=[validators.validate_longitude],
                                    verbose_name='Долгота')

    latitude = models.DecimalField(max_digits=7,
                                   decimal_places=5,
                                   null=False,
                                   blank=False,
                                   validators=[validators.validate_latitude],
                                   verbose_name='Широта')

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
    # TODO: проверку для значений (повторное использование критерия только для типа диапазон)
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

    class Meta:
        verbose_name = 'Критерий для места'
        verbose_name_plural = 'критерии для места'

    def __str__(self) -> str:
        return f'{self.criterion.internal_name}'


class Route(UpdateDescriptionMixin, models.Model):
    """ Маршрут """
    name = models.CharField(max_length=255,
                            null=False,
                            blank=False,
                            verbose_name='Наименование')

    details = models.JSONField(null=True,
                               blank=True,
                               verbose_name='Описание маршрута')

    places = models.ManyToManyField(Place,
                                    related_name='routes',
                                    verbose_name='Места')

    criteria = models.ManyToManyField(Criterion,
                                      through='RouteCriterion',
                                      related_name='routes',
                                      verbose_name='Критерии')

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True,
                               on_delete=models.SET_NULL,
                               related_name='routes',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'маршруты'

    def __str__(self) -> str:
        return self.name


class RouteCriterion(models.Model):
    # TODO: проверку для значений (повторное использование критерия только для типа диапазон)
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

    class Meta:
        verbose_name = 'Критерий для маршрута'
        verbose_name_plural = 'критерии для маршрута'

    def __str__(self) -> str:
        return self.criterion.internal_name


class Guide(UpdateDescriptionMixin, models.Model):
    """ Путеводитель """
    route = models.OneToOneField(Route,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 related_name='guide',
                                 verbose_name='Маршрут')

    description = fields.RichTextField(null=True,
                                       blank=True,
                                       verbose_name='Описание')

    image = models.ImageField(upload_to='guides/',
                              null=True,
                              blank=True,
                              verbose_name='Файл')

    class Meta:
        verbose_name = 'Путеводитель'
        verbose_name_plural = 'путеводители'

    def __str__(self) -> str:
        return f'Путеводитель к маршруту "{self.route.name}"'
