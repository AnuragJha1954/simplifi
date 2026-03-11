from django.contrib import admin
from .models import (
    CreditCard,
    EMI,
    Subscription,
    MonthlySpending,
    FinancialGoal
)
from django.utils.html import format_html
from decimal import Decimal
from datetime import date

# -------------------------
# CREDIT CARD ADMIN
# -------------------------

@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = (
        "bank_name",
        "user",
        "total_limit",
        "available_limit",
        "interest_rate",
        "utilization_display",
        "created_at",
    )
    list_filter = ("bank_name", "interest_rate", "created_at")
    search_fields = ("bank_name", "user__username")
    ordering = ("-created_at",)

    def utilization_display(self, obj):
        return f"{obj.utilization_percentage():.2f}%"
    utilization_display.short_description = "Utilization"


# -------------------------
# EMI ADMIN
# -------------------------

@admin.register(EMI)
class EMIAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "principal_amount",
        "monthly_payment",
        "interest_rate",
        "remaining_months",
        "total_remaining_display",
        "created_at",
    )
    list_filter = ("interest_rate", "created_at")
    search_fields = ("name", "user__username")
    ordering = ("-created_at",)

    def total_remaining_display(self, obj):
        return obj.total_remaining()
    total_remaining_display.short_description = "Total Remaining"


# -------------------------
# SUBSCRIPTION ADMIN
# -------------------------

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "monthly_cost",
        "is_essential",
    )
    list_filter = ("is_essential",)
    search_fields = ("name", "user__username")


# -------------------------
# MONTHLY SPENDING ADMIN
# -------------------------

@admin.register(MonthlySpending)
class MonthlySpendingAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "user",
        "average_monthly_amount",
    )
    search_fields = ("category", "user__username")


# -------------------------
# FINANCIAL GOAL ADMIN
# -------------------------

@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "user",
        "goal_type",
        "target_amount",
        "current_amount",
        "monthly_contribution",
        "expected_annual_return",
        "target_date",
        "created_at",
    )

    list_filter = (
        "goal_type",
        "created_at",
    )

    search_fields = (
        "name",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = ("-created_at",)

    list_per_page = 20