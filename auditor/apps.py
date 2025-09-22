from django.apps import AppConfig


class AuditorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditor'
    
    def ready(self):
        import main_home.signals
