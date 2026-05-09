from django.db import models


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