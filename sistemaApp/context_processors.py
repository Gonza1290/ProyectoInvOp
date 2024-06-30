# sistemaApp/context_processors.py

from django.apps import apps
from django.urls import NoReverseMatch, reverse

def admin_app_list(request):
    app_list = []
    for app in apps.get_app_configs():
        models = []
        for model in app.get_models():
            try:
                url = reverse(f'admin:{app.label}_{model._meta.model_name}_changelist')
                # Capitalizar la primera letra del modelo
                model_name = model._meta.verbose_name_plural.capitalize()
                models.append({
                    'name': model_name,
                    'url': url,
                })
            except NoReverseMatch:
                continue
        if models:
            # Ordenar los modelos alfabéticamente por nombre
            models = sorted(models, key=lambda x: x['name'])
            app_list.append({
                'name': app.verbose_name,
                'models': models
            })
    return {'admin_app_list': app_list}
