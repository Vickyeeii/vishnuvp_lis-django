from django.contrib import admin
from .models import TestCategory, LabTest


@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = [
        'test_name',
        'test_code',
        'category',
        'sample_type',
        'price',
        'status'
    ]

    list_filter = [
        'category',
        'sample_type',
        'status'
    ]

    search_fields = [
        'test_name',
        'test_code'
    ]