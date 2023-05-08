from typing import List, Tuple

import pytest

from django.contrib.auth.models import AbstractUser

from route_settings_builder import models, queries


M2M_COUNT = 3


pytestmark = [pytest.mark.django_db]


def test_add_place_to_route(admin_user):
    """ Проверка запроса на добавление места в маршрут """
    route = _create_route(admin_user)
    place = _create_places()[0]

    route = queries.add_place_to_route(route, place.uuid)
    place.refresh_from_db()

    assert place in route.places.all()
    assert route in place.routes.all()


def test_remove_place_from_route(admin_user):
    """ Проверка запроса на удаление места из маршрута """
    route = _create_route(admin_user)
    places = _create_places()

    route.places.add(*places)

    route = queries.remove_place_from_route(route, places[0].uuid)
    places[0].refresh_from_db()

    route_places = route.places.all()
    assert places[0] not in route_places
    assert route not in places[0].routes.all()

    for place in places[1:]:
        assert place in route_places


def test_add_criterion_to_route(admin_user):
    """ Проверка запроса на добавление критерия в маршрут """
    route = _create_route(admin_user)
    criterion = _create_criteria()[0]

    criterion_data = {
        'internal_name': criterion.internal_name,
        'value': 'test',
    }

    queries.add_criterion_to_route(route, criterion_data)

    route.refresh_from_db()

    assert criterion in route.criteria.all()
    assert route in criterion.routes.all()
    assert models.RouteCriterion.objects.filter(criterion=criterion, route=route,
                                                value=criterion_data['value']).exists()


def test_edit_route_criterion(admin_user):
    """ Проверка запроса на редактирование критерия маршрута """
    route = _create_route(admin_user)
    criteria = _create_criteria()

    route, route_criteria = _relate_criterion_to_route(route, criteria)

    new_route_criterion_data = {'internal_name': criteria[0].internal_name, 'value': 'not testing anymore'}
    queries.edit_route_criterion(route, new_route_criterion_data)

    route.refresh_from_db()

    route_criteria[0].refresh_from_db()
    assert route_criteria[0].value == new_route_criterion_data['value']

    for criterion in criteria:
        assert criterion in route.criteria.all()


def test_delete_criterion_from_route(admin_user):
    """ Проверка запроса на удаление критерия из маршрута """
    route = _create_route(admin_user)
    criteria = _create_criteria()

    route, route_criteria = _relate_criterion_to_route(route, criteria)
    route_criterion_internal_name = criteria[0].internal_name

    queries.remove_criterion_from_route(route, route_criterion_internal_name)

    route.refresh_from_db()

    assert criteria[0] not in route.criteria.all()
    assert route not in criteria[0].routes.all()
    assert not models.RouteCriterion.objects.filter(id=route_criteria[0].id)


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


def _relate_criterion_to_route(route: models.Route,
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
            route=route, criterion=criterion, value=f'test {criterion.internal_name}'))

    route.refresh_from_db()

    return route, route_criteria
