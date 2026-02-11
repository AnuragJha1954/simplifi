from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class CreditCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    total_limit = models.DecimalField(max_digits=12, decimal_places=2)
    available_limit = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.FloatField(help_text="Annual interest rate (%)", default=36)
    created_at = models.DateTimeField(auto_now_add=True)

    def utilization_percentage(self):
        used = self.total_limit - self.available_limit
        return (used / self.total_limit) * 100 if self.total_limit else 0

    def __str__(self):
        return f"{self.bank_name} - {self.user.username}"


class EMI(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.FloatField()
    remaining_months = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def total_remaining(self):
        return self.monthly_payment * self.remaining_months

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_essential = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class MonthlySpending(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    average_monthly_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.category}"



class FinancialGoal(models.Model):

    GOAL_TYPES = [
        ("emergency", "Emergency Fund"),
        ("travel", "Travel"),
        ("home", "Home"),
        ("retirement", "Retirement"),
        ("custom", "Custom"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    goal_type = models.CharField(
        max_length=20,
        choices=GOAL_TYPES,
        default="custom"
    )

    name = models.CharField(max_length=100)

    target_amount = models.DecimalField(max_digits=12, decimal_places=2)

    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    timeline_months = models.PositiveIntegerField(
        help_text="How many months to complete this goal"
    )

    monthly_contribution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(default=timezone.now)

    # Intelligent calculations

    def required_monthly(self):
        remaining = self.target_amount - self.current_amount
        if self.timeline_months > 0:
            return remaining / self.timeline_months
        return 0

    def predicted_completion_date(self):
        if self.monthly_contribution <= 0:
            return None

        remaining = self.target_amount - self.current_amount
        months = remaining / self.monthly_contribution
        return timezone.now().date() + timedelta(days=int(months * 30))

    def progress_percent(self):
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100

    def __str__(self):
        return self.name