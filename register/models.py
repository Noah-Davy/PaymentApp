from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ('GBP', 'British Pound'),
        ('EUR', 'Euro'),
        ('USD', 'US Dollar'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="GBP")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
