from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

from lazydrf.utils import register_app


#: Defines the DRF router.
Router = routers.DefaultRouter()

## Register model endpoints for the sample Django application:
register_app("sample", Router)

#: Defines the URL patterns:
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r"^", include(Router.urls)),
]
