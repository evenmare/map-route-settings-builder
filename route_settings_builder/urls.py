from django.contrib import admin
from django.urls import path

from route_settings_builder.api import api


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', api.urls),
]
