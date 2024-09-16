from django.urls import path
from .views import (
    RegisterAPIView, LoginAPIView, 
    UserAPIView, RefreshTokenAPIView, 
    LogoutAPIView, ForgetPasswordAPIView, 
    ResetPasswordAPIView )

urlpatterns = [
    path('register', RegisterAPIView.as_view(), name='register_view'),
    path('login', LoginAPIView.as_view(), name='login_view'),
    path('user', UserAPIView.as_view(), name='user_view'),
    path('refresh', RefreshTokenAPIView.as_view(), name='refresh_token_view'),
    path('logout', LogoutAPIView.as_view(), name='logout_view'),
    path('forgetpassword', ForgetPasswordAPIView.as_view(), name='forget_password_view'),
    path('resetpassword', ResetPasswordAPIView.as_view(), name='password_reset')
]