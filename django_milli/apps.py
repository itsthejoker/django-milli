from django.apps import AppConfig
from django.db.models.signals import post_save, pre_delete

from .signals import post_save_handler, pre_delete_handler


class DjangoMilliConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_milli"
    verbose_name = "Django Milli"

    def ready(self):
        post_save.connect(post_save_handler)
        pre_delete.connect(pre_delete_handler)
