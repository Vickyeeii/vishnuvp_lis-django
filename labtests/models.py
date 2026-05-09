from django.db import models
from accounts.models import CustomUser


class TestCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class LabTest(models.Model):

    SAMPLE_CHOICES = (
        ('blood', 'Blood'),
        ('urine', 'Urine'),
        ('stool', 'Stool'),
        ('saliva', 'Saliva'),
        ('swab', 'Swab'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    category = models.ForeignKey(
        TestCategory,
        on_delete=models.CASCADE,
        related_name='tests'
    )
    test_name = models.CharField(max_length=200)
    test_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    sample_type = models.CharField(
        max_length=50,
        choices=SAMPLE_CHOICES
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    turnaround_time = models.CharField(
        max_length=100,
        help_text="Example: 24 Hours"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_name} ({self.test_code})"

class SampleCollection(models.Model):

    CONDITION_CHOICES = (
        ('good', 'Good'),
        ('damaged', 'Damaged'),
        ('hemolyzed', 'Hemolyzed'),
    )

    STATUS_CHOICES = (
        ('collected', 'Collected'),
        ('received', 'Received in Lab'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    )

    order = models.OneToOneField(
    'orders.LabOrder',
        on_delete=models.CASCADE,
        related_name='sample'
    )

    sample_id = models.CharField(
        max_length=100,
        unique=True
    )

    collected_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'phlebotomist'}
    )

    collection_date = models.DateTimeField(
        auto_now_add=True
    )

    sample_condition = models.CharField(
        max_length=30,
        choices=CONDITION_CHOICES,
        default='good'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='collected'
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.sample_id