from .handlers import admission_handlers, auth_handlers

EVENT_MAP = {
    "admission_approved": [
        admission_handlers.send_welcome_message,
        admission_handlers.log_admission,
    ],
    "quiz_completed": [
        auth_handlers.update_progress,
    ],
}

def emit_event(event_type, data):
    handlers = EVENT_MAP.get(event_type, [])

    for handler in handlers:
        try:
            handler(data)
        except Exception as e:
            print(f"Error in handler {handler.__name__}: {e}")