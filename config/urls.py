from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Здесь позже добавим URL приложения mailing
    # path('', include('mailing.urls')),
]