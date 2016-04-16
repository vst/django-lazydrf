from django.db import models

from lazydrf.models import LDRF


class Record(models.Model, metaclass=LDRF):
    """
    Defines a key/value record model.
    """

    #: Defines the key of the record.
    key = models.CharField(max_length=16, unique=True, blank=False, null=False)

    #: Defines the value of the record.
    value = models.CharField(max_length=64, blank=False, null=False, db_index=True)

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
