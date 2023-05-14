from envparse import env


RMQ_HOST = env.str('RMQ_HOST', default='localhost')
RMQ_PORT = env.int('RMQ_PORT', default=5672)
RMQ_PREFETCH_COUNT = env.int('RMQ_PREFETCH_COUNT', default=10)

RMQ_USER = env.str('RMQ_USER', default='guest')
RMQ_PASSWORD = env.str('RMQ_PASSWORD', default='guest')
RMQ_QUEUE = env.str('RMQ_QUEUE')
RMQ_URL_QUERY_PARAMS = env.str('RMQ_URL_QUERY_PARAMS', default='')

RMQ_URL = f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}:{RMQ_PORT}/?{RMQ_URL_QUERY_PARAMS}"
