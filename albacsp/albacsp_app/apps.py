from django.apps import AppConfig
import threading
import time

class AlbacspAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'albacsp_app'

    def ready(self):
        import albacsp_app.signals
        from .utils import update_device_vuln

        def periodic_task():
            while True:
                update_device_vuln()
                time.sleep(60)

        thread = threading.Thread(target=periodic_task, daemon=True)
        thread.start()
