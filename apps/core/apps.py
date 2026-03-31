# qubitgyanpro\apps\core\apps.py

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        import apps.core.signals

        from events import register_all_events
        register_all_events()