# qubitgyanpro\apps\core\admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.core.constants import UserRole

from apps.core.models import (
    User,
    UserProfile,
    StudentProfile,
    StaffProfile,
    AdminProfile,
    StaffPermission
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-date_joined',)

    list_display = (
        'email', 'role', 'status', 'is_active',
        'mfa_enabled', 'telegram_verified', 'is_deleted'
    )

    list_filter = (
        'role', 'status', 'is_active',
        'is_verified', 'mfa_enabled', 'is_deleted'
    )

    search_fields = ('email', 'telegram_user_id', 'telegram_username', 'id')

    readonly_fields = (
        'id', 'last_login', 'date_joined', 'last_activity',
        'failed_login_attempts', 'last_login_ip', 'login_count',
        'deleted_at', 'created_by', 'updated_by',
        'terms_accepted_at', 'privacy_policy_accepted_at'
    )

    fieldsets = (
        (_('Authentication'), {
            'fields': ('email', 'password', 'mfa_enabled', 'password_changed_at')
        }),
        (_('Classification'), {
            'fields': ('role', 'status')
        }),
        (_('State flags'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'is_verified', 'is_onboarded', 'is_deleted'
            )
        }),
        (_('Security Tracking'), {
            'fields': (
                'failed_login_attempts', 'account_locked_until',
                'last_login_ip', 'last_device', 'login_count'
            )
        }),
        (_('Audit'), {
            'fields': (
                'created_by', 'updated_by',
                'date_joined', 'last_activity',
                'deleted_at',
                'terms_accepted_at', 'privacy_policy_accepted_at'
            )
        }),
        (_('Telegram Integration'), {
            'fields': (
                'telegram_user_id', 'telegram_chat_id',
                'telegram_username', 'telegram_verified',
                'telegram_linked_at'
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'status'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.role in [UserRole.ADMIN, UserRole.STAFF]:
            obj.is_staff = True
        else:
            obj.is_staff = False

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'city', 'country', 'timezone')
    search_fields = ('user__email', 'full_name', 'phone_number', 'emergency_contact_name')
    list_filter = ('country', 'timezone', 'locale')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrollment_id', 'academic_status', 'target_exam', 'batch_year')
    search_fields = ('user__email', 'enrollment_id', 'institution_name')
    list_filter = ('academic_status', 'batch_year', 'preferred_language')


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'designation', 'employment_type')
    search_fields = ('user__email', 'employee_id', 'department', 'designation')
    list_filter = ('department', 'employment_type')
    autocomplete_fields = ('reporting_manager',)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_tier', 'super_admin', 'system_notifications_enabled')
    list_filter = ('admin_tier', 'super_admin', 'system_notifications_enabled')


@admin.register(StaffPermission)
class StaffPermissionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'role_level', 'can_approve_admissions',
        'can_edit_content', 'can_manage_users',
        'can_view_reports', 'can_manage_billing'
    )

    list_filter = (
        'role_level', 'can_approve_admissions', 'can_edit_content',
        'can_manage_users', 'can_view_reports', 'can_manage_billing',
        'can_manage_roles', 'can_export_data'
    )

    search_fields = ('user__email',)

    readonly_fields = ('permissions_updated_at',)

    autocomplete_fields = ('permissions_updated_by',)

    