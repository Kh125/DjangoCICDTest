from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from django.core.mail import send_mail
import datetime, random, string

from .middleware import JWTAuthentication
from .serializers import UserSerializer, UserInfoSerializer
from .models import User, UserToken, PasswordReset
from .auth_services import create_access_token, create_refresh_token, decode_refresh_token

class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        serialier = UserSerializer(data=data)
        serialier.is_valid(raise_exception=True)
        serialier.save()

        return Response(serialier.data)

class LoginAPIView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        
        user = User.objects.filter(username=username).first()

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid credentials!")
        
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Invalid credentials")
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Check the refresh token for this user already exists
        user_token = UserToken.objects.filter(user_id = user.id)

        if user_token.exists():
            user_token.delete()

        # Save Refresh Token
        UserToken.objects.create(
            user_id=user.id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )

        response = Response()

        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'token': access_token
        }

        return response
    
class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    def get(self, request):
        return Response(UserInfoSerializer(request.user).data)
    
class RefreshTokenAPIView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        user_id = decode_refresh_token(refresh_token)

        if not UserToken.objects.filter(
            user_id=user_id,
            token=refresh_token,
            expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
        ).exists():
            raise exceptions.AuthenticationFailed("Unauthenticated! Invalid refresh token.")

        access_token = create_access_token(user_id)

        return Response({
            'token': access_token
        })
    
class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        UserToken.objects.filter(token=refresh_token).delete()

        response = Response()
        response.delete_cookie(key='refresh_token')
        response.data = {
            'message': 'Logout success'
        }

        return response
    
class ForgetPasswordAPIView(APIView):
    def post(self, request):
        try:
            email=request.data['email']

            if not User.objects.filter(email=email).exists():
                raise exceptions.NotFound("There is no registered user with this email!")

            token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

            PasswordReset.objects.create(
                email=request.data['email'],
                token=token
            )

            url = 'http://localhost:3000/reset/' + token

            send_mail(
                subject='Password Reset',
                message='Click here %s to reset your password.' % url,
                from_email='from@example.com',
                recipient_list=[email]
            )

            return Response({
                'message': 'Password reset sent!'
            })
        
        except Exception as e:
            raise exceptions.APIException(str(e))

class ResetPasswordAPIView(APIView):
    def post(self, request):
        data = request.data

        reset_password = PasswordReset.objects.filter(token=data['token']).first()

        if not reset_password:
            raise exceptions.APIException('Invalid Token!')
        
        user = User.objects.filter(email=reset_password.email).first()

        if not user:
            raise exceptions.APIException('User not found!')
        
        user.set_password(data['password'])
        user.save()

        return Response({
            'message': 'Password reset is successful!'
        })
        