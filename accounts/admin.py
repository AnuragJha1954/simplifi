from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    
    # Add custom fields to list display
    list_display = (
        'username',
        'email',
        'phone',
        'income_range',
        'is_staff',
        'is_active',
    )

    # Add filters
    list_filter = (
        'is_staff',
        'is_active',
        'income_range',
    )

    # Add search
    search_fields = (
        'username',
        'email',
        'phone',
    )

    # Fieldsets for edit page
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("phone", "income_range"),
        }),
    )

    # Fieldsets for add user page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {
            "fields": ("phone", "income_range"),
        }),
    )