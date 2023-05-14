import decimal
from typing import List, Tuple, Optional, Set

import pytest

from django.contrib.auth.models import AbstractUser

from route_settings_builder import models, models_utils


M2M_COUNT = 3


pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize('route_data', [
    {'name': 'test_name'},
    {'name': 'test_name', 'criteria': [{'criterion_id': 2, 'value': 't'}]},
    {'name': 't', 'places': [1, 2]},
    {'name': 'f', 'criteria': [{'criterion_id': 0, 'value': 'te'}], 'places': [1]},
])
def test_create_route(admin_user, route_data):
    """ Проверка логики на создание маршрута """
    places = _create_places()
    criteria = _create_criteria()

    route_data['author'] = admin_user

    route_data, criteria_ids, places_ids = _set_route_data_relations_by_ids(route_data, criteria, places)
    route = models_utils.create_or_update_route(route_data)

    assert route.is_draft is True
    assert route.name == route_data['name']

    _assert_route_relations(route, criteria_ids, places_ids)


@pytest.mark.parametrize('route_data', [
    {'name': 'new test', 'criteria': [{'criterion_id': 1, 'value': 'so'}]},
    {'places': [1], 'guide_description': 'description'},
    {'criteria': [{'criterion_id': 1, 'value': 'so'}], 'places': [1]},
    {'criteria': [], 'details': {'some': 'test'}},
])
def test_update_route(admin_user, route_data):
    """ Проверка логики на обновление маршрута """
    route = _create_route(admin_user)
    places = _create_places()
    criteria = _create_criteria()

    route, _ = _relate_criteria_to_route(route, [criteria[0]])
    route, _ = _relate_places_to_route(route, [places[0]])

    route_data['author'] = admin_user
    route_data, criteria_ids, places_ids = _set_route_data_relations_by_ids(route_data, criteria, places)

    route = models_utils.create_or_update_route(route_data, route.uuid)

    assert route.is_draft is False if route_data.get('details') else True

    if route_data.pop('criteria', None) is None:
        criteria_ids = {criteria[0].id}
    if route_data.pop('places', None) is None:
        places_ids = {places[0].id}

    _assert_route_relations(route, criteria_ids, places_ids)

    for field_name, value in route_data.items():
        assert getattr(route, field_name) == value


def test_get_points_coordinates_from_places(admin_user):
    """ Проверка запроса на получение списка точек маршрута """
    route = _create_route(admin_user)
    places = _create_places()

    _relate_places_to_route(route, places)

    points_coordinates = models_utils.get_points_coordinates_from_route_places(route)
    assert isinstance(points_coordinates, list)
    assert isinstance(points_coordinates[0], tuple)
    assert isinstance(points_coordinates[0][0], float)


def test_get_criteria_from_route(admin_user):
    """ Проверка запроса на получение перечня критериев со значениями """
    route = _create_route(admin_user)
    criteria = _create_criteria()
    criteria.append(models.Criterion.objects.create(internal_name='-10', value_type='numeric', name='numeric'))

    route, route_criteria = _relate_criteria_to_route(route, criteria)

    route_criteria_with_values = models_utils.get_criteria_from_route(route)

    for route_criterion in route_criteria[:-1]:
        assert route_criteria_with_values[route_criterion.criterion.internal_name] == route_criterion.value

    assert route_criteria_with_values[route_criteria[-1].criterion.internal_name] == float(route_criteria[-1].value)


def _assert_route_relations(route: models.Route, criteria_ids: Optional[Set[int]], places_ids: Optional[Set[int]]):
    """
    Проверка наличия всех необходимых связей
    :param route: маршрут
    :param criteria_ids: множество id критериев
    :param places_ids: множество id мест
    :return: None
    """
    if criteria_ids:
        assert set(route.criteria.values_list('id', flat=True)) == criteria_ids

    if places_ids:
        assert set(route.places.values_list('id', flat=True)) == places_ids


def _create_route(user: AbstractUser) -> models.Route:
    """
    Создание маршрута
    :param user: пользователь
    :return: маршрут
    """
    return models.Route.objects.create(name='test', author=user)


def _create_places() -> List[models.Place]:
    """
    Создание мест
    :return: список мест
    """
    places = [models.Place.objects.create(name=str(i), latitude=i * 10, longitude=i * 10) for i in range(M2M_COUNT)]
    return places


def _create_criteria() -> List[models.Criterion]:
    """
    Создание критериев
    :return: список критериев
    """
    criteria = [models.Criterion.objects.create(name=str(i), internal_name=str(i)) for i in range(M2M_COUNT)]
    return criteria


def _relate_criteria_to_route(route: models.Route,
                              criteria: List[models.Criterion]) -> Tuple[models.Route, List[models.RouteCriterion]]:
    """
    Привязка критериев к маршруту
    :param route: маршрут
    :param criteria: список критериев
    :return: маршрут, список объектов связи маршрута и критериев
    """
    route_criteria = []

    for criterion in criteria:
        route_criteria.append(models.RouteCriterion.objects.create(
            route=route, criterion=criterion, value=str(int(criterion.internal_name) + 10)))

    route.refresh_from_db()

    return route, route_criteria


def _relate_places_to_route(route: models.Route,
                            places: List[models.Place]) -> Tuple[models.Route, List[models.RoutePlace]]:
    """
    Привязка мест к маршруту
    :param route: маршрут
    :param places: места
    :return: маршрут, список объектов связи маршрута и мест
    """
    route_places = []

    for place in places:
        route_places.append(models.RoutePlace.objects.create(route=route, place=place))

    route.refresh_from_db()

    return route, route_places


def _set_route_data_relations_by_ids(route_data: dict, criteria: Optional[List[models.Criterion]],
                                     places: Optional[List[models.Place]]) -> Tuple[dict, set, set]:
    """

    :param route_data: данные маршрута
    :param criteria: список инстансов Criterion
    :param places: список инстансов Place
    :return: route_data, множество id связанных критериев, множество id связанных мест
    """
    criteria_ids = set()
    places_ids = set()

    if criteria_data := route_data.get('criteria'):
        route_data['criteria'] = [{'criterion_id': criteria[criterion_data['criterion_id']].id,
                                   'value': criterion_data['value']}
                                  for criterion_data in criteria_data
                                  if criteria_ids.add(criteria[criterion_data['criterion_id']].id) is None]

    if places_data := route_data.get('places'):
        route_data['places'] = [places[place_id].id for place_id in places_data
                                if places_ids.add(places[place_id].id) is None]

    return route_data, criteria_ids, places_ids
