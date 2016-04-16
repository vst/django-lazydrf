from django.db.models import Model, CharField
from django_filters.filters import LOOKUP_TYPES
from rest_framework.decorators import list_route
from rest_framework.fields import SerializerMethodField

from lazydrf.models import LDRF


class TestBase(Model, metaclass=LDRF):
    """
    Defines a base model.
    """

    #: Defines a name attribute.
    name = CharField(max_length=8)

    class Meta:
        app_label = "lazydrf"
        abstract = True

    class APIFields:
        editable = ["name"]
        readable = ["id"]
        declared = {
            "idplus1": SerializerMethodField(),
            "get_idplus1": lambda serializer, obj: obj.id + 1
        }
        ordering = ["id", "name"]
        searching = ["name"]

    class APIFiltering:
        id = ["exact", "lt", "lte", "gt", "gte"]
        name = LOOKUP_TYPES

    class APIViewset:
        readonly = True

        @list_route
        def justname(self, request):
            return self.model.objects.values_list("name")


class TestSubclass(TestBase):
    """
    Defines a subclass of the base model.
    """

    #: Defines a value attribute.
    value = CharField(max_length=8)

    class Meta:
        app_label = "lazydrf"
        abstract = True

    class APIFields:
        editable = ["value"]
