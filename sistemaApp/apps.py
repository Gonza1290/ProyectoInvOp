from django.apps import AppConfig
from django.db.models.signals import post_migrate

class SistemaappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sistemaApp'

    def ready(self):
        from .signals import inicializar_estados, create_groups_and_permissions
        # Conectar las funciones a la señal post_migrate
        post_migrate.connect(inicializar_estados, sender=self)
        post_migrate.connect(create_groups_and_permissions, sender=self)