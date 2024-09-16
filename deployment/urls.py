from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def hello_world(request):
    return HttpResponse("Hello world from Django updated with supervisor command include!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hello_world),
    path('api/v1/', include('apis.urls')),
    path('api/v1/auth/', include('app.urls'))
]
