from django.apps import AppConfig


class AlbacspAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'albacsp_app'

    def ready(self):
        import albacsp_app.signals