# qubitgyanpro\events\__init__.py

from events.handlers.admission_handlers import register_admission_handlers


def register_all_events():
    register_admission_handlers()