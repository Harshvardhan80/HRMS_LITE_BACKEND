from django.db import models
from django.core.validators import EmailValidator
import re
from django.core.exceptions import ValidationError


def validate_employee_id(value):
    """Validate employee ID format"""
    if not re.match(r'^[A-Z0-9]+$', value):
        raise ValidationError('Employee ID must contain only uppercase letters and numbers')


class Employee(models.Model):
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_employee_id],
        help_text='Unique employee identifier'
    )
    full_name = models.CharField(
        max_length=100,
        help_text='Full name of the employee'
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text='Email address of the employee'
    )
    department = models.CharField(
        max_length=100,
        help_text='Department name'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

    def save(self, *args, **kwargs):
        # Convert employee_id to uppercase before saving
        self.employee_id = self.employee_id.upper()
        # Convert email to lowercase before saving
        self.email = self.email.lower()
        super().save(*args, **kwargs)


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['employee', 'date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} - {self.status}"
