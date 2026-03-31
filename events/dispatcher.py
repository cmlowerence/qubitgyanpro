# qubitgyanpro\events\dispatcher.py

import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

_EVENT_HANDLERS: Dict[str, List[Callable]] = {}


def register_event(event_type: str, handler: Callable):
    if event_type not in _EVENT_HANDLERS:
        _EVENT_HANDLERS[event_type] = []

    _EVENT_HANDLERS[event_type].append(handler)


def dispatch_event(event_type: str, payload: dict):
    handlers = _EVENT_HANDLERS.get(event_type, [])

    for handler in handlers:
        try:
            handler(payload)
        except Exception:
            logger.exception(f"[EVENT ERROR] {event_type} → {handler.__name__}")