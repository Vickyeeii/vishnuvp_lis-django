from django.contrib import admin
from .models import TestCategory, LabTest, SampleCollection


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

@admin.register(SampleCollection)
class SampleCollectionAdmin(admin.ModelAdmin):

    list_display = [
        'sample_id',
        'order',
        'collected_by',
        'sample_condition',
        'status',
        'collection_date'
    ]

    list_filter = [
        'sample_condition',
        'status',
        'collection_date'
    ]

    search_fields = [
        'sample_id',
        'order__patient__first_name',
        'order__patient__last_name'
    ]