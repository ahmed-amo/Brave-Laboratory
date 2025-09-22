from django.apps import AppConfig


class ClientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'client'
    
    def ready(self):
        import main_home.signals

    