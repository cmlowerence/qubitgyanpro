# qubitgyanpro\events\apps.py

from django.apps import AppConfig
from events.dispatcher import register_event
from events.event_types import EventType

from events.handlers.recommendation_handlers import handle_lesson_completed


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'

    def ready(self):
        from events.handlers.admission_handlers import register_admission_handlers

        register_admission_handlers()
        register_event(EventType.LESSON_COMPLETED, handle_lesson_completed)

