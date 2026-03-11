from django.contrib import admin
from .models import (
    ChildProfile,
    ChildWallet,
    ExpenseCategory,
    AllocationHistory,
    FundRequest,
    AllowanceHistory
)


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ("child_user", "parent", "age", "is_active", "created_at")
    search_fields = ("child_user__username", "parent__username")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ChildWallet)
class ChildWalletAdmin(admin.ModelAdmin):
    list_display = ("child", "total_allocated", "last_updated")
    search_fields = ("child__child_user__username",)
    readonly_fields = ("last_updated",)


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "child", "allocated_amount", "created_at")
    search_fields = ("name", "child__child_user__username")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


@admin.register(AllocationHistory)
class AllocationHistoryAdmin(admin.ModelAdmin):
    list_display = ("child", "category", "amount", "action", "created_at")
    search_fields = ("child__child_user__username", "category__name")
    list_filter = ("action", "created_at")
    readonly_fields = ("created_at",)


@admin.register(FundRequest)
class FundRequestAdmin(admin.ModelAdmin):
    list_display = ("child", "category", "amount", "status", "created_at", "reviewed_at")
    search_fields = ("child__child_user__username", "category__name")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "reviewed_at")


@admin.register(AllowanceHistory)
class AllowanceHistoryAdmin(admin.ModelAdmin):
    list_display = ("child", "category", "amount", "action", "created_at")
    search_fields = ("child__child_user__username", "category__name")
    list_filter = ("action", "created_at")
    readonly_fields = ("created_at",)