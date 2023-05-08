# pylint: disable=too-few-public-methods,missing-class-docstring
from typing import List, Optional

from ninja import Schema, ModelSchema, Field

from route_settings_builder import models


class PlaceSchema(ModelSchema):
    """ Схема к сущности места """
    longitude: float
    latitude: float

    class Config:
        model = models.Place
        model_fields = ('uuid', 'name', 'longitude', 'latitude', )


class CriterionSchema(ModelSchema):
    """ Схема к сущности критерия """
    class Config:
        model = models.Criterion
        model_fields = ('internal_name', 'name', 'value_type', )


class NestedCriterionSchema(Schema):
    """ Схема связи к сущности критерия """
    criterion: CriterionSchema
    value: str


class DetailedPlaceSchema(PlaceSchema):
    """ Схема детализации сущности места """
    criteria: List[NestedCriterionSchema] = Field([], alias='placecriterion_set')

    class Config:
        model = models.Place
        model_fields = ('uuid', 'name', 'longitude', 'latitude', )


class ListRouteSchema(ModelSchema):
    """ Схема сущности маршрута для перечня """
    is_draft: bool

    class Config:
        model = models.Route
        model_fields = ('uuid', 'updated_at', 'name', )


class DetailedRouteSchema(ListRouteSchema):
    """ Схема детализации сущности маршрута """
    criteria: List[NestedCriterionSchema] = Field([], alias='routecriterion_set')
    details: Optional[dict]
    places: List[PlaceSchema]

    class Config:
        model = models.Route
        model_fields = ('uuid', 'updated_at', 'name', 'details', 'places', )


class WriteRouteSchema(ModelSchema):
    """ Схема создания и редактирования для сущности маршрута """

    class Config:
        model = models.Route
        model_fields = ('name', )


class PlaceToRouteSchema(ModelSchema):
    """ Схема добавления места в маршрут """

    class Config:
        model = models.Place
        model_fields = ('uuid', )


class CriterionToRouteSchema(Schema):
    """ Схема добавления критерия в маршрут """
    internal_name: str
    value: str


class UpdateRouteCriterion(Schema):
    """ Схема обновления критерия в маршруте """
    value: str
