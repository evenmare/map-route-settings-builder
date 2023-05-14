# TODO: оптимизация запросов
import decimal
import uuid
from typing import Tuple, List, Optional

from django.db import transaction
from django.db.models import F, Case, When, ExpressionWrapper, FloatField, BooleanField
from django.db.models.functions import Cast

from route_settings_builder import models


@transaction.atomic
def create_or_update_route(route_data: dict, route_uuid: Optional[uuid.UUID] = None):
    """ Создание или обновление маршрута """
    route_data = dict(route_data)

    criteria_data = route_data.pop('criteria', None)
    places_ids = route_data.pop('places', None)

    is_create_operation = False
    existed_criteria_ids = set()
    existed_places_ids = set()

    if not route_uuid:
        is_create_operation = True
        route = models.Route.objects.create(author=route_data.pop('author'), **route_data)
    else:
        models.Route.objects.filter(author=route_data.pop('author'), uuid=route_uuid).update(**route_data)
        route = models.Route.objects.select_for_update().get(uuid=route_uuid)
        existed_criteria_ids = set(route.criteria.values_list('id', flat=True) if not is_create_operation else [])
        existed_places_ids = set(route.places.values_list('id', flat=True) if not is_create_operation else [])

    added_criteria_ids = []
    if criteria_data is not None:
        for criterion_data in criteria_data:
            models.RouteCriterion.objects.create(**criterion_data, route=route)
            added_criteria_ids.append(criterion_data['criterion_id'])

    if places_ids is not None:
        models.RoutePlace.objects.bulk_create([models.RoutePlace(place_id=place_id, route=route)
                                               for place_id in places_ids])

    if not is_create_operation:
        if criteria_data is not None:
            if remove_criteria_ids := existed_criteria_ids - set(added_criteria_ids):
                models.RouteCriterion.objects.filter(criterion__id__in=remove_criteria_ids).delete()

        if places_ids is not None:
            if remove_places_ids := existed_places_ids - set(places_ids):
                models.RoutePlace.objects.filter(place__id__in=remove_places_ids).delete()

    route.refresh_from_db()
    setattr(route, 'is_draft', bool(route.details))

    return route


def get_points_coordinates_from_route_places(route: models.Route) -> List[Tuple[decimal.Decimal]]:
    """
    Получение списка координат мест из маршрута
    :param route: маршрут
    :return: список координат
    """
    return list(route.places.values_list(ExpressionWrapper(F('latitude'), output_field=FloatField()),
                                         ExpressionWrapper(F('longitude'), output_field=FloatField())))


def get_criteria_from_route(route: models.Route) -> dict:
    """
    Получение перечня критериев значений
    :param route: маршрут
    :return: словарь вида {критерий: значение}
    """
    return {line[0]: line[1 if line[1] is not None else 2 if line[2] is not None else 3]
            for line in route.criteria
            .annotate(numeric_value=Case(When(value_type='numeric',
                                              then=Cast('routecriterion__value', FloatField())),
                                         defalt=None),
                      boolean_value=Case(When(value_type='boolean',
                                              then=Cast('routecriterion__value', BooleanField())),
                                         default=None))
            .values_list('internal_name', 'numeric_value', 'boolean_value', 'routecriterion__value')}
