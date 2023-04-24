from typing import Union
import decimal

from django.core.exceptions import ValidationError


NumericType = Union[int, float, decimal.Decimal]


def validate_longitude(value: NumericType) -> None:
    """
    Проверка значения долготы.
    Вызывает ValidationError, если значение неверно.

    :param value: значение долготы
    :return: None
    """
    if value < -180 or value > 180:
        raise ValidationError('Долгота не может по модулю превышать 180!')


def validate_latitude(value: NumericType) -> None:
    """
    Проверка значения широты.
    Вызывает ValidationError, если значение неверно.

    :param value: значение широты
    :return: None
    """
    if value < -90 or value > 90:
        raise ValidationError('Широта не может по модулю превышать 90!')
