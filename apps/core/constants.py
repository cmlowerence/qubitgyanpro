# qubitgyanpro\apps\core\constants.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRole(models.TextChoices):
    STUDENT = "STUDENT", _("Student")
    STAFF = "STAFF", _("Staff")
    ADMIN = "ADMIN", _("Admin")

class UserStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    SUSPENDED = "SUSPENDED", _("Suspended")
    PENDING = "PENDING", _("Pending")
    LOCKED = "LOCKED", _("Locked")

class Gender(models.TextChoices):
    MALE = "MALE", _("Male")
    FEMALE = "FEMALE", _("Female")
    OTHER = "OTHER", _("Other")
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY", _("Prefer Not to Say")

class EmploymentType(models.TextChoices):
    FULL_TIME = "FULL_TIME", _("Full Time")
    PART_TIME = "PART_TIME", _("Part Time")
    CONTRACT = "CONTRACT", _("Contract")
    INTERN = "INTERN", _("Intern")

class AcademicStatus(models.TextChoices):
    GOOD_STANDING = "GOOD_STANDING", _("Good Standing")
    PROBATION = "PROBATION", _("Probation")
    ALUMNI = "ALUMNI", _("Alumni")
    WITHDRAWN = "WITHDRAWN", _("Withdrawn")

class AdminTier(models.TextChoices):
    SUPERUSER = "SUPERUSER", _("Superuser")
    SYSTEM_ADMIN = "SYSTEM_ADMIN", _("System Admin")
    SECURITY_AUDITOR = "SECURITY_AUDITOR", _("Security Auditor")
