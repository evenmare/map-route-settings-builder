# TODO: оптимизация запросов
from typing import Union
import uuid

from route_settings_builder import models


def add_place_to_route(route: models.Route, place_uuid: Union[uuid.UUID, str]) -> models.Route:
    """
    Добавление места маршрута
    :param route: маршрут
    :param place_uuid: UUID объекта места
    :return: маршрут
    """
    place = models.Place.objects.get(uuid=place_uuid)
    route.places.add(place)
    return route


def remove_place_from_route(route: models.Route, place_uuid: Union[uuid.UUID, str]) -> models.Route:
    """
    Удаление места из маршрута
    :param route: маршрут
    :param place_uuid: UUID объекта места
    :return: маршрут
    """
    place = models.Place.objects.get(uuid=place_uuid)
    route.places.remove(place)
    return route


def add_criterion_to_route(route: models.Route, criterion_data: dict) -> None:
    """
    Добавление критерия в маршрут
    :param route: маршрут
    :param criterion_data: данные критерия вида {'internal_name': str, 'value': str}
    :return: None
    """
    criterion = models.Criterion.objects.get(internal_name=criterion_data['internal_name'])

    value = _validate_value(criterion, value=criterion_data['value'])

    models.RouteCriterion.objects.create(criterion=criterion, route=route, value=value)


def edit_route_criterion(route: models.Route, criterion_data: dict) -> None:
    """
    Редактирование критерия маршрута
    :param route: маршрут
    :param criterion_data: данные критерия вида {'internal_name': str, 'value': str}
    :return: None
    """
    route_criterion = models.RouteCriterion.objects.get(route=route,
                                                        criterion__internal_name=criterion_data['internal_name'])

    value = _validate_value(route_criterion.criterion.value_type, value=criterion_data['value'])

    route_criterion.value = value
    route_criterion.save()


def remove_criterion_from_route(route: models.Route, criterion_internal_name: str) -> None:
    """
    Удаление критерия из маршрута
    :param route: маршрут
    :param criterion_internal_name: internal_name критерия
    :return: None
    """
    criterion = models.Criterion.objects.get(internal_name=criterion_internal_name)
    route.criteria.remove(criterion)


def _validate_value(value_type: str, value: str) -> str:
    """
    Валидация значения критерия маршрута
    :param value_type: тип значения
    :param value: значение
    :return: значение
    """
    if value_type == 'numeric' and not value.replace('.', '', 1).isdigit():
        raise ValueError('"value" должен быть числом!')

    return value
