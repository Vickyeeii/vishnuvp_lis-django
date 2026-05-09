from django.contrib import admin
from .models import ResultEntry


@admin.register(ResultEntry)
class ResultEntryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'status',
        'entered_by',
        'verified_by',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'order__patient__mrn',
        'entered_by__username',
    )