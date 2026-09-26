class CacheControlMiddleware:
    """
    Middleware для клиентского кеширования.
    Добавляет заголовки Cache-Control к ответам.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Кешируем статические файлы на 1 год
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=31536000, immutable'

        # Кешируем страницу товаров / главную на 5 минут
        elif request.path == '/' or request.path.startswith('/mailings/'):
            if not request.user.is_authenticated:
                response['Cache-Control'] = 'public, max-age=300'

        return response