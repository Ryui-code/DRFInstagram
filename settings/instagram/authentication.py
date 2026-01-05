from rest_framework.authentication import BaseAuthentication
from .models import UserProfile

class CookieTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('auth_token')
        if not token:
            return None
        try:
            user = UserProfile.objects.get(token=token)
        except UserProfile.DoesNotExist:
            return None
        return user, None