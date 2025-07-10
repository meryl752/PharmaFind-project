from django.utils import timezone
from .models import User

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(last_seen=timezone.now())
        return self.get_response(request) 