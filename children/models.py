from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ChildProfile(models.Model):

    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="children"
    )

    child_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="child_profile"
    )

    age = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.child_user} (Child of {self.parent})"


class ChildWallet(models.Model):

    child = models.OneToOneField(
        ChildProfile,
        on_delete=models.CASCADE,
        related_name="wallet"
    )

    total_allocated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.child.child_user}'s Wallet"


class ExpenseCategory(models.Model):

    child = models.ForeignKey(
        ChildProfile,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(max_length=200)

    allocated_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("child", "name")

    def __str__(self):
        return f"{self.name} - {self.child.child_user}"


class AllocationHistory(models.Model):

    child = models.ForeignKey(
        ChildProfile,
        on_delete=models.CASCADE,
        related_name="allocation_history"
    )

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    action = models.CharField(
        max_length=50,
        choices=[
            ("added", "Added"),
            ("updated", "Updated")
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child.child_user} - {self.amount} ({self.action})"


class FundRequest(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    child = models.ForeignKey(
        ChildProfile,
        on_delete=models.CASCADE,
        related_name="fund_requests"
    )

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    reason = models.TextField()

    parent_note = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )




class AllowanceHistory(models.Model):

    ACTION_TYPES = [
        ("added", "Allowance Added"),
        ("request_approved", "Request Approved"),
        ("request_rejected", "Request Rejected"),
    ]

    child = models.ForeignKey(
        ChildProfile,
        on_delete=models.CASCADE,
        related_name="allowance_history"
    )

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_TYPES
    )

    note = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child.child_user.username} - {self.action} - {self.amount}"

