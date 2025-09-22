from django.apps import AppConfig


class ReceptionistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'receptionist'

    def ready(self):
        import main_home.signals