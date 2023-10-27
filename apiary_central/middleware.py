from django.http import JsonResponse
from .models import ApiaryHub

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f'Request data = {request.data()}')
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return JsonResponse({'error': 'API key missing'}, status=401)

        try:
            hub = ApiaryHub.objects.get(api_key=api_key)
        except ApiaryHub.DoesNotExist:
            return JsonResponse({'error': 'Invalid API key'}, status=401)

        response = self.get_response(request)
        return response
