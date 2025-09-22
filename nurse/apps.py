from django.apps import AppConfig


class NurseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nurse'

    def ready(self):
        import main_home.signals