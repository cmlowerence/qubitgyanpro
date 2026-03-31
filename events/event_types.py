# qubitgyanpro\events\event_types.py

class EventType:
    ADMISSION_CREATED = "admission.created"
    ADMISSION_APPROVED = "admission.approved"
    ADMISSION_REJECTED = "admission.rejected"
    ADMISSION_UNDER_REVIEW = "admission.under_review"

    USER_REGISTERED = "user.registered"
    PASSWORD_RESET_REQUESTED = "auth.password_reset_requested"
    QUIZ_COMPLETED = "assessment.quiz_completed"