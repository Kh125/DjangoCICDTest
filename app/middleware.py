from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions
from .auth_services import decode_access_token
from .models import User

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')
            user_id = decode_access_token(token)

            user = User.objects.get(pk=user_id)

            return (user, None)
        
        raise exceptions.AuthenticationFailed('Unauthenticated md!')