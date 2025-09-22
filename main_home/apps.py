from django.apps import AppConfig


class MainHomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_home'
    
    def ready(self):
        import main_home.signals
