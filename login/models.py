from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Make email unique
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('normal', 'Normal'),
    ]
    
    class Meta:
        db_table = 'user'  # Set the table name to 'user'

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to custom user model
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    start_date = models.DateTimeField(auto_now_add=True)  # Track when the subscription started
    end_date = models.DateTimeField(null=True, blank=True)  # Optional expiration date
    is_active = models.BooleanField(default=True)  # If the subscription is active
    credits = models.IntegerField(default=0)  # Number of credits available (if using a credits system)

    def __str__(self):
        return f"{self.user.username} - {self.plan} Plan"