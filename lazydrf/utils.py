from django.apps import apps


def register_app(appname, router):
    """
    Registers all lazydrf models in a Djangoi application with the provided router.
    """

    ## Iterate over the models for the given application name:
    for model in apps.get_app_config(appname).get_models():
        ## If does not have LDRFMeta, skip:
        if not hasattr(model, "LDRFMeta"):
            continue

        ## Register the endpoint:
        model.LDRFMeta.register(router)
