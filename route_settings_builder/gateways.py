import uuid

from django.conf import settings
import aio_pika

from mq_misc.amqp import ReplyToConsumer, create_weak_publisher

from route_settings_builder import models


class ReplyToRouteBuilderConsumer(ReplyToConsumer):
    """ Consumer, создающийся для обработки запроса """
    route_uuid: uuid.UUID

    def __init__(self, route_uuid: uuid.UUID, *args, **kwargs) -> None:
        """
        :param route_uuid: UUID маршрута
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.route_uuid = route_uuid

    async def process_message(self, body: dict, raw_message: aio_pika.IncomingMessage) -> None:
        """
        Обработка сообщения
        :param body: тело response
        :param raw_message: "сырое" сообщение
        :return: None
        """
        await models.Route.objects.filter(uuid=self.route_uuid).aupdate(details=body)


async def build_route(route_uuid: uuid.UUID, request: dict) -> None:
    """
    Построение маршрута
    :param route_uuid: UUID маршрута
    :param request: запрос
    :return: None
    """
    params = {'url': settings.RMQ_URL, 'queue_name': 'route-settings-builder'}

    async with create_weak_publisher(settings.RMQ_URL, settings.RMQ_QUEUE) as publisher:
        request_consumer = ReplyToRouteBuilderConsumer(route_uuid, **params)
        await request_consumer.create_consume_connection()
        await request_consumer.publish(request, publisher)
