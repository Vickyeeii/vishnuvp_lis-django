from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

def validate_dob(value):
    today = date.today()
    if value > today:
        raise ValidationError("Date of birth cannot be in the future.")
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 0 or age > 150:
        raise ValidationError(f"Invalid age ({age} years). Age must be between 0 and 150 years.")

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
    date_of_birth = models.DateField(validators=[validate_dob])
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