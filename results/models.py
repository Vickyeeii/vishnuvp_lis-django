from django.db import models
from orders.models import LabOrder
from accounts.models import CustomUser


class ResultEntry(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('entered', 'Entered'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
    )

    order = models.ForeignKey(
        LabOrder,
        on_delete=models.CASCADE,
        related_name='results'
    )

    result_value = models.TextField()

    normal_range = models.CharField(
        max_length=100
    )

    unit = models.CharField(
        max_length=50
    )

    entered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='entered_results'
    )

    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_results'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Result #{self.id} - {self.order}"