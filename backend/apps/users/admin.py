from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, StudentProfile, TeacherProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email', 'username', 'role', 'is_active',
        'failed_login_attempts', 'two_factor_enabled'
    )
    list_filter = (
        'role', 'is_active', 'is_staff',
        'two_factor_enabled', 'must_change_password'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Informations personnelles'), {
            'fields': (
                'username', 'first_name', 'last_name',
                'role', 'phone_number', 'date_of_birth',
                'address', 'profile_picture'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        (_('Sécurité'), {
            'fields': (
                'failed_login_attempts', 'account_locked_until',
                'must_change_password', 'password_changed_at',
                'two_factor_enabled', 'last_login_ip'
            )
        }),
        (_('Dates importantes'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'role', 'is_staff', 'is_active'
            )
        }),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'student_id', 'enrollment_date',
        'current_semester', 'major'
    )
    list_filter = ('enrollment_date', 'current_semester')
    search_fields = (
        'user__email', 'user__username',
        'student_id', 'major'
    )
    raw_id_fields = ('user',)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'employee_id', 'department',
        'specialization', 'hire_date'
    )
    list_filter = ('hire_date', 'department')
    search_fields = (
        'user__email', 'user__username',
        'employee_id', 'department', 'specialization'
    )
    raw_id_fields = ('user',)
