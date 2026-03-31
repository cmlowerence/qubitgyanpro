# qubitgyanpro\events\handlers\admission_handlers.py

from events.dispatcher import register_event
from events.event_types import EventType
from services.telegram_service import send_message


def handle_admission_created(payload: dict):
    admission = payload.get("admission")

    if not admission or not admission.telegram_user_id:
        return

    send_message(
        telegram_id=admission.telegram_user_id,
        text=f"📩 Admission received for {admission.full_name}. We will review it shortly."
    )


def handle_admission_under_review(payload: dict):
    admission = payload.get("admission")

    if not admission or not admission.telegram_user_id:
        return

    send_message(
        telegram_id=admission.telegram_user_id,
        text="🕵️ Your admission is under review."
    )


def handle_admission_approved(payload: dict):
    admission = payload.get("admission")

    if not admission or not admission.telegram_user_id:
        return

    send_message(
        telegram_id=admission.telegram_user_id,
        text="🎉 Your admission has been approved! Please set your password to continue."
    )


def handle_admission_rejected(payload: dict):
    admission = payload.get("admission")

    if not admission or not admission.telegram_user_id:
        return

    reason = admission.rejection_reason or "No reason provided."

    send_message(
        telegram_id=admission.telegram_user_id,
        text=f"❌ Admission rejected.\nReason: {reason}"
    )


def register_admission_handlers():
    register_event(EventType.ADMISSION_CREATED, handle_admission_created)
    register_event(EventType.ADMISSION_UNDER_REVIEW, handle_admission_under_review)
    register_event(EventType.ADMISSION_APPROVED, handle_admission_approved)
    register_event(EventType.ADMISSION_REJECTED, handle_admission_rejected)