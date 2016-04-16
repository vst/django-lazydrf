import inspect

from django.db.models.base import ModelBase
from django_filters import MethodFilter, FilterSet
from rest_framework import filters
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet


class LDRFMeta:
    """
    Defines a lazydrf metadata class.
    """

    def __init__(self, model):
        self.__model = model
        self.__meta = getattr(model, "_meta")
        self.__name = self.__meta.model_name
        self.__abstract = hasattr(self.__meta, "abstract") and self.__meta.abstract

    @property
    def model(self):
        """
        Returns the model class.

        :return: The model class.
        """
        return self.__model

    @property
    def meta(self):
        """
        Returns the model's meta specification.

        :return: The model's meta specification.
        """
        return self.__meta

    @property
    def name(self):
        """
        Returns the canonical name of the model.

        :return: The canonical name of the model.
        """
        return self.__name

    @property
    def abstract(self):
        """
        Indicates if the model is abstract.

        :return: `True` if the model is abstract, `False` otherwise.
        """
        return self.__abstract

    @property
    def serializer(self):
        """
        Returns the serializer of the model.

        Note that a runtime error is raised if the serializer is not set yet.

        :return: The serializer of the model.
        """
        if not hasattr(self, "__serializer"):
            raise RuntimeError("Serializer for the model {} is not defined yet.".format(self.name))
        return getattr(self, "__serializer")

    @serializer.setter
    def serializer(self, value):
        """
        Sets the serializer of the model.

        Note that a runtime error is raised if the serializer is already set.

        :param value: The serializer.
        """
        if hasattr(self, "__serializer"):
            raise RuntimeError("Serializer is already set.")
        setattr(self, "__serializer", value)

    @property
    def ordering(self):
        """
        Returns the ordering of the model.

        Note that a runtime error is raised if the ordering is not set yet.

        :return: The ordering of the model.
        """
        if not hasattr(self, "__ordering"):
            raise RuntimeError("Ordering for the model {} is not defined yet.".format(self.name))
        return getattr(self, "__ordering")

    @ordering.setter
    def ordering(self, value):
        """
        Sets the ordering of the model.

        Note that a runtime error is raised if the ordering is already set.

        :param value: The ordering.
        """
        if hasattr(self, "__ordering"):
            raise RuntimeError("Ordering is already set.")
        setattr(self, "__ordering", value)

    @property
    def searching(self):
        """
        Returns the searching of the model.

        Note that a runtime error is raised if the searching is not set yet.

        :return: The searching of the model.
        """
        if not hasattr(self, "__searching"):
            raise RuntimeError("Searching for the model {} is not defined yet.".format(self.name))
        return getattr(self, "__searching")

    @searching.setter
    def searching(self, value):
        """
        Sets the searching of the model.

        Note that a runtime error is raised if the searching is already set.

        :param value: The searching.
        """
        if hasattr(self, "__searching"):
            raise RuntimeError("Searching is already set.")
        setattr(self, "__searching", value)

    @property
    def filtering(self):
        """
        Returns the filtering of the model.

        Note that a runtime error is raised if the filtering is not set yet.

        :return: The filtering of the model.
        """
        if not hasattr(self, "__filtering"):
            raise RuntimeError("Filtering for the model {} is not defined yet.".format(self.name))
        return getattr(self, "__filtering")

    @filtering.setter
    def filtering(self, value):
        """
        Sets the filtering of the model.

        Note that a runtime error is raised if the filtering is already set.

        :param value: The filtering.
        """
        if hasattr(self, "__filtering"):
            raise RuntimeError("Filtering is already set.")
        setattr(self, "__filtering", value)

    @property
    def viewset(self):
        """
        Returns the viewset of the model.

        Note that a runtime error is raised if the viewset is not set yet.

        :return: The viewset of the model.
        """
        if not hasattr(self, "__viewset"):
            raise RuntimeError("Viewset for the model {} is not defined yet.".format(self.name))
        return getattr(self, "__viewset")

    @viewset.setter
    def viewset(self, value):
        """
        Sets the viewset of the model.

        Note that a runtime error is raised if the viewset is already set.

        :param value: The viewset.
        """
        if hasattr(self, "__viewset"):
            raise RuntimeError("Viewset is already set.")
        setattr(self, "__viewset", value)

    def _get_filter_class(self):
        """
        Process the filtering information and constructs a FilterSet.

        :return: FilterSet class.
        """
        ## Declare fields and attributes:
        fields = dict()
        attrs = dict()

        ## Iterate over the filtering attributes and processes them:
        for member in inspect.getmembers(self.filtering):
            ## If hidden, skip:
            if member[0].startswith("__"):
                continue

            ## Get name of the field and the value:
            key, value = member

            ## If value is callable, create a method for it:
            if hasattr(value, "__call__"):
                ## Define the method name:
                method = "filter_for_{}".format(key)

                ## Set the method:
                attrs[method] = value

                ## Set the field:
                attrs[key] = MethodFilter(action=method)
            else:
                fields[key] = value

        ## Set meta:
        attrs["Meta"] = type("Meta", (object,), {"model": self.model, "fields": fields})

        ## Create the filterset and return:
        return type("APIFilterBase", (FilterSet,), attrs)

    def register(self, router):
        """
        Registers the viewset to the router.
        """
        ## Set the filter class on the viewset:
        self.viewset.filter_class = self._get_filter_class()

        ## Now, register:
        router.register(self.viewset.uri, self.viewset)


class LDRF(ModelBase):
    """
    Defines a metaclass to process Django models and create DRF ModelViewSets.
    """

    #: Defines the attributes of interest.
    API_META_ATTRS = ["APIFields", "APIFiltering", "APIViewset"]

    #: Defines APIFields attributes and their defaults:
    API_FIELDS_ATTRS = [("editable", list),
                        ("readable", list),
                        ("declared", dict),
                        ("ordering", list),
                        ("searching", list)]

    #: Defines APIFields attributes and their defaults:
    API_VIEWSET_ATTRS = [
        ("readonly", lambda: False),
    ]

    def __new__(mcs, name, bases, attrs, **kwargs):
        """
        Processes the model provided with name, base classes, class attributes and additional
        keyword arguments provided to the `class` statement and injects the LDRFMeta instance
        as _ldrfmeta attribute.

        :param name: The name of the model.
        :param bases: Base classes of the model.
        :param attrs: Model class attributes.
        :param kwargs: Keyword arguments provided to the `class` statement when declaring the model.
        :return: The processed model class.
        """

        ## Check API attributes of interest, create if they don't exist:
        for attr in mcs.API_META_ATTRS:
            if attr not in attrs:
                attrs[attr] = type(attr, (object,), {})

        ## Get fields of interest:
        api_fields = mcs.extract_api_fields(attrs)
        api_filtering = mcs.extract_api_filtering(attrs)
        api_viewset = mcs.extract_api_viewset(attrs)

        ## Get the model class from super and return:
        model = super(LDRF, mcs).__new__(mcs, name, bases, attrs, **kwargs)

        ## Set the LDRFMeta attribute:
        model.LDRFMeta = LDRFMeta(model)

        ## Set the serializer:
        model.LDRFMeta.serializer = LDRF.build_serializer(model, api_fields, bases)

        ## Set the ordering:
        model.LDRFMeta.ordering = LDRF.build_ordering(model, api_fields, bases)

        ## Set the searching:
        model.LDRFMeta.searching = LDRF.build_searching(model, api_fields, bases)

        ## Set the filtering:
        model.LDRFMeta.filtering = LDRF.build_filtering(model, api_filtering, bases)

        ## Set the viewset:
        model.LDRFMeta.viewset = LDRF.build_viewset(model, api_viewset, bases)

        ## Done, return the model:
        return model

    @classmethod
    def build_serializer(cls, model, spec, bases):
        """
        Builds a serializer for the model with base classes from the specification.

        :param model: The model.
        :param spec: Serializer specification.
        :param bases: Base classes of the model.
        :return: A ModelSerializer instance.
        """
        ## Get the meta specification from the base models.
        base_serializers = [e for e in [cls.get_serializer(base) for base in bases] if e is not None]

        ## Extract fields from base serializers:
        fields = [field for base in base_serializers for field in base.Meta.fields]

        ## Extrace read-only fields from base serializers:
        fields_readable = [field for base in base_serializers for field in getattr(base.Meta, "read_only_fields", [])]

        ## Add current fields:
        fields = fields + spec.readable + spec.editable
        fields_readable = fields_readable + spec.readable

        ## Define attrs:
        attrs = {
            "Meta": type("Meta", (object,), {
                "model": model,
                "fields": list(fields),
                "read_only_fields": list(fields_readable),
            })
        }

        ## Update attributes with the declared fields and their companions:
        attrs.update(spec.declared)

        ## Done, create the serializer and return:
        return type("Serializer", tuple(base_serializers) or (ModelSerializer,), attrs)

    @classmethod
    def build_ordering(mcs, model, spec, bases):
        """
        Returns ordering fields.

        :param model: The model.
        :param spec: Ordering specification.
        :param bases: Base classes of the model.
        :return: A list of ordering fields.
        """
        return [field for base in bases for field in mcs.get_ordering(base)] + spec.ordering

    @classmethod
    def build_searching(mcs, model, spec, bases):
        """
        Returns search fields.

        :param model: The model.
        :param spec: Searching specification.
        :param bases: Base classes of the model.
        :return: A list of searching fields.
        """
        return [field for base in bases for field in mcs.get_searching(base)] + spec.searching

    @classmethod
    def build_filtering(cls, model, spec, bases):
        """
        Builds a filtering for the model with base classes from the specification.

        :param model: The model.
        :param spec: Filtering specification.
        :param bases: Base classes of the model.
        :return: A plain class.
        """
        ## Get the meta specification from the base models.
        base_filters = [e for e in [cls.get_filtering(base) for base in bases] if e is not None]

        ## Get the attributes of interest from the spec:
        attrs = dict([field for field in inspect.getmembers(spec) if not field[0].startswith("__")])

        ## Extend bases and return:
        return type("Filtering", tuple(base_filters), attrs)

    @classmethod
    def build_viewset(cls, model, spec, bases):
        """
        Builds a filtering for the model with base classes from the specification.

        :param model: The model.
        :param spec: Filtering specification.
        :param bases: Base classes of the model.
        :return: A plain class.
        """
        ## Get the viewsets from the base models.
        base_viewsets = [e for e in [cls.get_viewset(base) for base in bases] if e is not None]

        ## Declare attributes.
        attrs = dict()

        ## Set the model:
        attrs["model"] = model

        ## Set the uri:
        attrs["uri"] = "{}s".format(model.LDRFMeta.name)

        ## Set the serializer class:
        attrs["serializer_class"] = model.LDRFMeta.serializer

        ## Add filtering backends for the rest of the specifications:
        attrs["filter_backends"] = (filters.OrderingFilter, filters.SearchFilter, filters.DjangoFilterBackend)

        ## Set ordering fields:
        attrs["ordering_fields"] = model.LDRFMeta.ordering

        ## Set the default ordering:
        if model.LDRFMeta.ordering:
            attrs["ordering"] = model.LDRFMeta.ordering[0]

        ## Set searching fields:
        attrs["search_fields"] = model.LDRFMeta.searching

        ## Set the filter class:
        attrs["_filter_class"] = model.LDRFMeta.filtering

        ## Sential queryset required for DjangoModelPermissions:
        if not model.LDRFMeta.abstract:
            attrs["queryset"] = model.objects.all()

        ## Update attributes from the spec:
        attrs.update(dict([field for field in inspect.getmembers(spec) if not field[0].startswith("__")]))

        ## Defines the base classes to extend:
        base_viewsets = tuple(base_viewsets) or (ReadOnlyModelViewSet if spec.readonly else ModelViewSet,)

        ## Done, create and return:
        return type("Viewset", base_viewsets, attrs)

    @classmethod
    def get_ldrfmeta(mcs, model):
        """
        Returns the LDRFMeta attribute of the model if any.

        :param model: The model from which the LDRFMeta to be extracted.
        :return: The LDRFMeta instance if any, `None` otherwise
        """
        return getattr(model, "LDRFMeta", None)

    @classmethod
    def get_serializer(mcs, model):
        """
        Returns the serializer from the model.

        :param model: The model from which the serializer to be extracted.
        :return: The serializer if any, `None` otherwise
        """
        return mcs.get_ldrfmeta(model) and model.LDRFMeta.serializer

    @classmethod
    def get_ordering(mcs, model):
        """
        Returns the ordering from the model.

        :param model: The model from which the ordering to be extracted.
        :return: The ordering if any, `None` otherwise
        """
        return (mcs.get_ldrfmeta(model) or []) and model.LDRFMeta.ordering

    @classmethod
    def get_searching(mcs, model):
        """
        Returns the searching from the model.

        :param model: The model from which the searching to be extracted.
        :return: The searching if any, `None` otherwise
        """
        return (mcs.get_ldrfmeta(model) or []) and model.LDRFMeta.searching

    @classmethod
    def get_filtering(mcs, model):
        """
        Returns the filtering from the model.

        :param model: The model from which the filtering to be extracted.
        :return: The filtering if any, `None` otherwise
        """
        return mcs.get_ldrfmeta(model) and model.LDRFMeta.filtering

    @classmethod
    def get_viewset(mcs, model):
        """
        Returns the viewset from the model.

        :param model: The model from which the viewset to be extracted.
        :return: The viewset if any, `None` otherwise
        """
        return mcs.get_ldrfmeta(model) and model.LDRFMeta.viewset

    @classmethod
    def extract_api_fields(mcs, attrs):
        """
        Extracts APIFields specification from the attributes.

        :param attrs: Model class attributes
        :return: APIFields class.
        """
        ## Pop API fields specification:
        spec = attrs.pop("APIFields")

        ## Add attributes if missing:
        for attr, default in mcs.API_FIELDS_ATTRS:
            if not hasattr(spec, attr):
                setattr(spec, attr, default())

        ## Done, return the spec:
        return spec

    @classmethod
    def extract_api_filtering(mcs, attrs):
        """
        Extracts APIFiltering specification from the attributes.

        :param attrs: Model class attributes
        :return: APIFiltering class.
        """
        return attrs.pop("APIFiltering")

    @classmethod
    def extract_api_viewset(mcs, attrs):
        """
        Extracts APIFiltering specification from the attributes.

        :param attrs: Model class attributes
        :return: APIFiltering class.
        """
        ## Pop API viewsets specification:
        spec = attrs.pop("APIViewset")

        ## Add attributes if missing:
        for attr, default in mcs.API_VIEWSET_ATTRS:
            if not hasattr(spec, attr):
                setattr(spec, attr, default())

        ## Done, return the spec:
        return spec
