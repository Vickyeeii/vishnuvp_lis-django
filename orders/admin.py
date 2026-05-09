from django.contrib import admin
from .models import LabOrder


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'patient',
        'physician',
        'priority',
        'status',
        'ordered_at'
    ]

    list_filter = [
        'priority',
        'status',
        'ordered_at'
    ]

    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'physician__username'
    ]

    filter_horizontal = ['tests']