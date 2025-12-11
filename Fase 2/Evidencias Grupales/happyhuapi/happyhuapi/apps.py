from django.apps import AppConfig
from django.conf import settings

class HappyhuapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'happyhuapi'

    def ready(self):
        # Registrar carpeta templates del proyecto
        import os
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        if templates_dir not in settings.TEMPLATES[0]['DIRS']:
            settings.TEMPLATES[0]['DIRS'].append(templates_dir)

