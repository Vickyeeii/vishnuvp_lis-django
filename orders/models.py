from django.db import models
from patients.models import Patient
from labtests.models import LabTest
from accounts.models import CustomUser


class LabOrder(models.Model):

    PRIORITY_CHOICES = (
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sample_collected', 'Sample Collected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    physician = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'physician'}
    )
    tests = models.ManyToManyField(
        LabTest,
        related_name='orders'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending'
    )
    clinical_notes = models.TextField(
        blank=True,
        null=True
    )
    ordered_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return f"Order #{self.id} - {self.patient}"