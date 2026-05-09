from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = (
        'mrn',
        'first_name',
        'last_name',
        'gender',
        'phone_number',
    )

    search_fields = (
        'mrn',
        'first_name',
        'last_name',
    )

    list_filter = (
        'gender',
    )