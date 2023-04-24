from ninja import NinjaAPI


api = NinjaAPI()


@api.get('/health')
@api.get('/health/')
def health_status(request):
    """ Проверка состояния сервиса """
    return {'status': 'ok'}
