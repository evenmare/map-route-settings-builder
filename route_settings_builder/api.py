from typing import List, Optional
import uuid

from asgiref.sync import sync_to_async

from django.shortcuts import render
from ninja import NinjaAPI, Query, pagination, errors
from ninja_apikey.security import APIKeyAuth

from route_settings_builder import models, schemas, filters, models_utils, gateways


auth = APIKeyAuth()  # TODO: bearer token авторизация
api = NinjaAPI(csrf=True, auth=auth)


class AsyncAPIKeyAuth(APIKeyAuth):  # pylint: disable=too-few-public-methods
    """ Асинхронная авторизация """

    @sync_to_async
    def authenticate(self, *args, **kwargs):
        return super().authenticate(*args, **kwargs)


@api.get('/health', auth=None)
def health_status(request):
    """ Проверка состояния сервиса """
    return {'status': 'ok'}


@api.get('/places', response={200: List[schemas.PlaceSchema]})
@pagination.paginate()
def get_places(request, request_filters: filters.PlaceFilterSchema = Query(...)):
    """ Получение перечня мест """
    places = models.Place.objects.all()
    places = request_filters.filter(places)
    return places


@api.get('/places/{place_id}', response=schemas.DetailedPlaceSchema)
def get_place(request, place_id: int):
    """ Получение места """
    try:
        # TODO: Оптимизация запросов к БД
        place = models.Place.objects.get(uuid=place_id)
    except models.Place.DoesNotExist as ex:
        raise errors.HttpError(404, 'Место не найдено') from ex

    return place


@api.get('/criteria', response=List[schemas.CriterionSchema])
def get_criteria(request, request_filters: filters.CriterionFilterSchema = Query(...)):
    """ Получение перечня критериев """
    criteria = models.Criterion.objects.all()
    criteria = request_filters.filter(criteria)
    return criteria


@api.get('/routes', response=List[schemas.ListRouteSchema])
@pagination.paginate()
def get_routes(request, request_filters: filters.RouteFilterSchema = Query(...)):
    """ Получение перечня мест """
    routes = models.Route.objects.filter(author=request.user).add_is_draft_field().all()
    routes = request_filters.filter(routes)
    return routes


@api.get('/routes/{route_uuid}', response=schemas.DetailedRouteSchema)
def get_route(request, route_uuid: uuid.UUID):
    """ Получение маршрута """
    return _get_route(request, route_uuid, prefetch=('places', ))


@api.post('/routes/', response=schemas.DetailedRouteSchema)
def create_route(request, payload: schemas.CreateRouteSchema):
    """ Создание маршрута """
    try:
        return _operate_route(request, payload.dict())
    except Exception as ex:
        raise errors.HttpError(400, str(ex)) from ex


@api.put('/routes/{route_uuid}/', response=schemas.DetailedRouteSchema)
def update_route(request, route_uuid: uuid.UUID, payload: schemas.CreateRouteSchema):
    """ Обновление маршрута """
    try:
        request_data = payload.dict()
        for not_required_field_name in ('guide_description', 'criteria'):
            if not_required_field_name not in request_data:
                request_data[not_required_field_name] = None

        return _operate_route(request, request_data, route_uuid)
    except models.Route.DoesNotExist as ex:
        raise errors.HttpError(404, 'Маршрут не найден') from ex
    except Exception as ex:
        raise errors.HttpError(400, str(ex)) from ex


@api.patch('/routes/{route_uuid}/', response=schemas.DetailedRouteSchema)
def partial_update_route(request, route_uuid: uuid.UUID, payload: schemas.UpdateRouteSchema):
    """ Частичное обновление маршрута """
    try:
        return _operate_route(request, payload.dict(exclude_unset=True), route_uuid)
    except models.Route.DoesNotExist as ex:
        raise errors.HttpError(404, 'Маршрут не найден') from ex
    except Exception as ex:
        raise errors.HttpError(400, str(ex)) from ex


@api.delete('/routes/{route_uuid}/', response={204: None}, auth=AsyncAPIKeyAuth())
async def remove_route(request, route_uuid: uuid.UUID):
    """ Удаление маршрута """
    await request.auth
    delete_count, _ = await models.Route.objects.filter(author=request.user, uuid=route_uuid).adelete()

    if not delete_count:
        raise errors.HttpError(404, 'Маршрут не найден')

    return 204, None


@api.post('/routes/{route_uuid}/build/', auth=AsyncAPIKeyAuth(), response={204: None})
async def build_route(request, route_uuid: uuid.UUID):
    """ Запрос на строительство маршрута """
    await request.auth

    try:
        route = await models.Route.objects.aget(author=request.user, uuid=route_uuid)
    except models.Route.DoesNotExist as ex:
        raise errors.HttpError(404, 'Маршрут не найден') from ex

    request = {
        'points_coordinates': await sync_to_async(models_utils.get_points_coordinates_from_route_places)(route),
        **await sync_to_async(models_utils.get_criteria_from_route)(route)
    }

    await gateways.build_route(route_uuid, request)


@api.get('/routes/{route_uuid}/guide/', response={200: str})
def get_route_guide(request, route_uuid: uuid.UUID):
    """ Запрос на получение гида """
    route = _get_route(request, route_uuid, add_draft_field=False, prefetch=('places', ))

    if guide_description := route.guide_description:
        return guide_description

    route_places = route.places.values('name', 'description')
    return render(request, 'guide.html', context={
        'route': route,
        'route_places': list(route_places),
    })


def _operate_route(request, route_data: dict, *args):
    """
    Добавление / обновление маршрута
    :param request: запрос
    :param payload: тело запроса
    :param args: аргументы обновления
    :return: маршрут
    """
    route_data['author'] = request.user
    return models_utils.create_or_update_route(route_data, *args)


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
