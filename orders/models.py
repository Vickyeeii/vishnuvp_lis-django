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
        (1, 'Ordered'),
        (2, 'Collected'),
        (3, 'In-Lab'),
        (4, 'Completed'),
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
        through='OrderLine',
        related_name='orders'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1
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

class OrderLine(models.Model):
    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE)
    assay = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderLine {self.id} - Order {self.order.id} - Assay {self.assay.id}"