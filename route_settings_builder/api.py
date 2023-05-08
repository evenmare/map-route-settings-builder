from typing import List, Optional
import uuid

from ninja import NinjaAPI, Query, pagination, errors
from ninja_apikey.security import APIKeyAuth

from route_settings_builder import models, schemas, filters, queries


auth = APIKeyAuth()  # TODO: bearer token авторизация
api = NinjaAPI(auth=auth)


@api.get('/health', auth=None)
def health_status(request):
    """ Проверка состояния сервиса """
    return {'status': 'ok'}


@api.get('/places', response={200: List[schemas.PlaceSchema]})
@pagination.paginate()
def get_places(request, request_filters: filters.PlaceFilterSchema = Query(...)):
    """
    Получение перечня мест
    :param request: запрос
    :param request_filters: фильтры запроса
    :return: перечень мест
    """
    places = models.Place.objects.all()
    places = request_filters.filter(places)
    return places


@api.get('/places/{place_uuid}', response=schemas.DetailedPlaceSchema)
def get_place(request, place_uuid: uuid.UUID):
    """
    Получение места
    :param request: запрос
    :param place_uuid: уникальный идентификатор места
    :return: место
    """
    try:
        # TODO: Оптимизация запросов к БД
        place = models.Place.objects.get(uuid=place_uuid)
    except models.Place.DoesNotExist as ex:
        raise errors.HttpError(404, 'Место не найдено') from ex

    return place


@api.get('/criteria', response=List[schemas.CriterionSchema])
def get_criteria(request, request_filters: filters.CriterionFilterSchema = Query(...)):
    """
    Получение перечня критериев
    :param request: запрос
    :param request_filters: фильтры запроса
    :return: перечень критериев
    """
    criteria = models.Criterion.objects.all()
    criteria = request_filters.filter(criteria)
    return criteria


@api.get('/routes', response=List[schemas.ListRouteSchema])
@pagination.paginate()
def get_routes(request, request_filters: filters.RouteFilterSchema = Query(...)):
    """
    Получение перечня мест
    :param request: запрос
    :param request_filters: фильтры запроса
    :return: перечень мест
    """
    routes = models.Route.objects.filter(author=request.user).add_is_draft_field().all()
    routes = request_filters.filter(routes)
    return routes


@api.get('/routes/{route_uuid}', response=schemas.DetailedRouteSchema)
def get_route(request, route_uuid: uuid.UUID):
    """
    Получение маршрута
    :param request: запрос
    :param route_uuid: уникальный идентификатор маршрута
    :return: маршрут
    """
    return _get_route(request, route_uuid, prefetch=('places', ))


@api.post('/routes/', response=schemas.DetailedRouteSchema)
def create_route(request, payload: schemas.WriteRouteSchema):
    """
    Создание маршрута
    :param request: запрос
    :param payload: тело запроса
    :return: маршрут
    """
    # TODO: логика на полное заполнение маршрута целиком
    route = models.Route.objects.create(**payload.dict(), author=request.user)
    setattr(route, 'is_draft', True)
    return route


# TODO: PUT / PATCH маршрута целиком


@api.delete('/routes/{route_uuid}/', response={204: None})
async def remove_route(request, route_uuid: uuid.UUID):
    """
    Удаление маршрута
    :param request: запрос
    :param route_uuid: uuid маршрута
    :return: None
    """
    count, _ = await models.Route.objects.filter(author=request.user, uuid=route_uuid).adelete()

    if not count:
        raise errors.HttpError(404, 'Маршрут не найден')

    return 204, None


@api.post('/routes/{route_uuid}/places/', response=schemas.DetailedRouteSchema)
def add_place_to_route(request, route_uuid: uuid.UUID, payload: schemas.PlaceToRouteSchema):
    """
    Добавление места в маршрут
    :param request: запрос
    :param route_uuid: uuid маршрута
    :param payload: тело запроса
    :return: маршрут
    """
    route = _get_route(request, route_uuid)

    try:
        route = queries.add_place_to_route(route, payload.dict()['uuid'])
    except models.Place.DoesNotExist as ex:
        raise errors.HttpError(404, 'Место не найдено') from ex

    return route


@api.delete('/routes/{route_uuid}/places/{place_uuid}/', response={204: None})
def remove_place_from_route(request, route_uuid: uuid.UUID, place_uuid: uuid.UUID):
    """
    Удаление места из маршрута
    :param request: запрос
    :param route_uuid: uuid маршрута
    :param place_uuid: uuid места
    :return: None
    """
    route = _get_route(request, route_uuid)

    try:
        queries.remove_place_from_route(route, place_uuid)
    except models.Place.DoesNotExist as ex:
        raise errors.HttpError(404, 'Место не найдено') from ex

    return 204, None


@api.post('/routes/{route_uuid}/criteria/', response=schemas.DetailedRouteSchema)
def add_criterion_to_route(request, route_uuid: uuid.UUID, payload: schemas.CriterionToRouteSchema):
    """
    Добавление критерия в маршрут
    :param request: запрос
    :param route_uuid: uuid маршрута
    :param payload: тело запроса
    :return: маршрут
    """
    route = _get_route(request, route_uuid)

    try:
        queries.add_criterion_to_route(route, dict(payload))
    except models.Criterion.DoesNotExist as ex:
        raise errors.HttpError(404, 'Критерий не найден') from ex

    route.refresh_from_db()
    return route


@api.patch('/routes/{route_uuid}/criteria/{criterion_internal_name}/', response=schemas.UpdateRouteCriterion)
def update_route_criterion(request,
                           route_uuid: uuid.UUID, criterion_internal_name: str, payload: schemas.UpdateRouteCriterion):
    """
    Обновление критерия в маршруте
    :param request: запрос
    :param route_uuid: uuid маршрута
    :param criterion_internal_name: внутреннее наименование маршрута
    :param payload: тело запроса
    :return: маршрут
    """
    route = _get_route(request, route_uuid)

    try:
        queries.edit_route_criterion(route, {**payload.dict(), **{'internal_name': criterion_internal_name}})
    except models.Criterion.DoesNotExist as ex:
        raise errors.HttpError(404, 'Критерий не найден') from ex

    route.refresh_from_db()
    return route


@api.delete('/routes/{route_uuid}/criteria/{criterion_internal_name}', response={204: None})
def remove_criterion_from_route(request, route_uuid: uuid.UUID, criterion_internal_name: str):
    """
    Удаление критерия из маршрута
    :param request: запрос
    :param route_uuid: uuid маршрута
    :param criterion_internal_name: внутреннее наименование критерия
    :return: None
    """
    route = _get_route(request, route_uuid)

    try:
        queries.remove_criterion_from_route(route, criterion_internal_name)
    except models.Criterion.DoesNotExist as ex:
        raise errors.HttpError(404, 'Критерий не найден') from ex

    return 204, None


def _get_route(request, route_uuid: uuid.UUID, add_draft_field: Optional[bool] = True,
               prefetch: Optional[tuple] = None) -> models.Route:
    """
    Запрос на получение маршрута по uuid
    :param route_uuid: значение uuid маршрута
    :return: маршрут
    """
    base_query = models.Route.objects.filter(author=request.user)

    if add_draft_field:
        base_query = base_query.add_is_draft_field()
    if prefetch:
        base_query = base_query.prefetch_related(*prefetch)

    try:
        # TODO: оптимизация запросов к БД
        route = base_query.get(uuid=route_uuid)
    except models.Route.DoesNotExist as ex:
        raise errors.HttpError(404, 'Маршрут не найден') from ex

    return route
