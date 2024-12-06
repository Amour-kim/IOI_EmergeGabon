from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, StudentProfile, TeacherProfile

class CustomUserAdmin(UserAdmin):
    list_display = (
        'email', 'username', 'first_name', 'last_name',
        'role', 'is_active', 'date_joined'
    )
    list_filter = (
        'role', 'is_active', 'is_staff',
        'two_factor_enabled',
        'date_joined'
    )
    search_fields = (
        'email', 'username', 'first_name',
        'last_name', 'phone_number'
    )
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {
            'fields': (
                'username', 'first_name', 'last_name',
                'role', 'phone_number', 'date_of_birth',
                'address', 'profile_picture', 'bio'
            )
        }),
        (_('Sécurité'), {
            'fields': (
                'failed_login_attempts', 'account_locked_until',
                'password_changed_at', 'two_factor_enabled',
                'last_login_ip'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
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
                'email', 'username', 'password1',
                'password2', 'role', 'is_staff',
                'is_active'
            )
        }),
    )

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'student_id', 'major',
        'current_semester', 'enrollment_date'
    )
    list_filter = ('major', 'current_semester', 'enrollment_date')
    search_fields = (
        'user__email', 'user__username',
        'student_id', 'major'
    )
    raw_id_fields = ('user',)

class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'employee_id', 'department',
        'specialization', 'hire_date'
    )
    list_filter = ('department', 'hire_date')
    search_fields = (
        'user__email', 'user__username',
        'employee_id', 'department', 'specialization'
    )
    raw_id_fields = ('user',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(TeacherProfile, TeacherProfileAdmin)
