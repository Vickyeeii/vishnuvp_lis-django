from django.db import models
from orders.models import LabOrder
from labtests.models import LabTest
from accounts.models import CustomUser


class ResultEntry(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('entered', 'Entered'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    )

    FLAG_CHOICES = (
        ('normal', 'Normal'),
        ('high', 'High'),
        ('low', 'Low'),
        ('critical', 'Critical'),
    )

    order = models.ForeignKey(
        LabOrder,
        on_delete=models.CASCADE,
        related_name='results'
    )

    test = models.ForeignKey(
        LabTest,
        on_delete=models.CASCADE,
        related_name='results',
        null=True,
        blank=True
    )

    result_value = models.TextField()

    normal_range = models.CharField(
        max_length=100,
        default='Normal',
        blank=True,
        null=True
    )

    unit = models.CharField(
        max_length=50,
        default='units',
        blank=True,
        null=True
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

    flag = models.CharField(
        max_length=20,
        choices=FLAG_CHOICES,
        default='normal'
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

    class Meta:
        unique_together = ('order', 'test')

    def __str__(self):
        return f"Result #{self.id} - Order {self.order.id} - Test {self.test.test_name if self.test else 'N/A'}"