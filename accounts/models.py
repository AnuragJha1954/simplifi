from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    ROLE_CHOICES = (
        ("parent", "Parent"),
        ("child", "Child"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="parent"
    )

    phone = models.CharField(max_length=15, blank=True)

    income_range = models.CharField(
        max_length=50,
        choices=[
            ('<5L', 'Below 5L'),
            ('5-10L', '5–10L'),
            ('10-25L', '10–25L'),
            ('25L+', '25L+'),
        ],
        blank=True
    )

    def __str__(self):
        return self.username
