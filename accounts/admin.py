from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username',
        'email',
        'role',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_staff',
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            'Additional Information',
            {
                'fields': (
                    'role',
                    'phone_number',
                )
            },
        ),
    )