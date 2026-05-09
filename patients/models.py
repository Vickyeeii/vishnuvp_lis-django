from django.db import models


class Patient(models.Model):

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    mrn = models.CharField(
        max_length=20,
        unique=True
    )
    first_name = models.CharField(
        max_length=100
    )
    last_name = models.CharField(
        max_length=100
    )
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )
    phone_number = models.CharField(
        max_length=15
    )
    email = models.EmailField(
        blank=True,
        null=True
    )
    address = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return f"{self.mrn} - {self.first_name} {self.last_name}"