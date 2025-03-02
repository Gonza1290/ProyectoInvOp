from django.apps import AppConfig
from django.db.models.signals import post_migrate

class SistemaappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sistemaApp'

    def ready(self):
        import sistemaApp.signals