from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    ROLE_CHOICES = (

        ('admin', 'Admin'),
        ('physician', 'Physician'),
        ('nurse', 'Nurse'),
        ('phlebotomist', 'Phlebotomist'),
        ('technician', 'Lab Technician'),

    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='nurse'
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} - {self.role}"