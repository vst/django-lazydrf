django-lazydrf
==============

``django-lazydrf`` is a dirty magic applied to your models to generate
automated `Django Rest Framework <http://www.django-rest-framework.org/>`_ endpoints.

    **Note** that this is an experimental project. Use at your own risk and sadness.

``TODO: Provide a complete README``

Installation
------------

::

    pip install django-lazydrf

Usage
-----

1. Define a Django model as follows::

    from django.db import models
    from django.db.models import CharField

    from lazydrf.models import LDRF


    class Record(models.Model, metaclass=LDRF):
        """
        Defines a key/value record model.
        """

        #: Defines the key of the record.
        key = CharField(max_length=16, unique=True, blank=False, null=False)

        #: Defines the value of the record.
        value = CharField(max_length=64, blank=False, null=False, db_index=True)

        class Meta:
            """
            Defines Django model metadata.
            """
            app_label = "sample"

        class APIFields:
            """
            Defines fields related API metadata.
            """
            editable = ["key", "value"]
            ordering = ["key"]
            searching = ["key", "^value"]

        class APIFiltering:
            """
            Defines filtering related API metadata.
            """
            key = ["exact", "icontains", "startswith"]
            value = ["exact", "icontains", "startswith"]

        class APIViewset:
            pass
            #readonly = True


2. Register all lazydrf models for a given Django application to the usual DRF router, like::

    from django.conf.urls import url, include
    from django.contrib import admin
    from rest_framework import routers

    from lazydrf.utils import register_app


    #: Defines the DRF router.
    Router = routers.DefaultRouter()

    ## Register model endpoints for the sample Django application:
    register_app("sample", Router)

    #: Defines URL patterns:
    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r"^", include(Router.urls)),
    ]
