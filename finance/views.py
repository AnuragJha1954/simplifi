from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import financial_summary,financial_summary, debt_free_projection, estimate_cibil
from .forms import CreditCardForm, EMIForm, SubscriptionForm, SpendingForm, FinancialGoalForm
from django.shortcuts import redirect
from .models import CreditCard, EMI, Subscription, MonthlySpending, FinancialGoal
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import date
from dateutil.relativedelta import relativedelta
import json


@login_required
def finance_overview(request):

    summary = financial_summary(request.user)
    debt_free_months = debt_free_projection(request.user)
    cibil_score = estimate_cibil(request.user)

    return render(request, 'finance/overview.html', {
        "summary": summary,
        "debt_free_months": debt_free_months,
        "cibil_score": cibil_score
    })





@login_required
def transactions(request):

    cards = CreditCard.objects.filter(user=request.user)
    emis = EMI.objects.filter(user=request.user)
    subs = Subscription.objects.filter(user=request.user)
    spendings = MonthlySpending.objects.filter(user=request.user)

    # Pagination for cards
    paginator = Paginator(cards, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Financial Summary
    total_credit_limit = cards.aggregate(
        total=Sum("total_limit")
    )["total"] or 0

    total_emi = emis.aggregate(
        total=Sum("monthly_payment")
    )["total"] or 0

    total_subscription = subs.aggregate(
        total=Sum("monthly_cost")
    )["total"] or 0

    context = {
        "card_form": CreditCardForm(),
        "emi_form": EMIForm(),
        "sub_form": SubscriptionForm(),
        "spend_form": SpendingForm(),
        "page_obj": page_obj,
        "total_credit_limit": total_credit_limit,
        "total_emi": total_emi,
        "total_subscription": total_subscription,
    }

    return render(request, "finance/transactions.html", context)


@require_POST
@login_required
def delete_card(request, pk):
    card = get_object_or_404(CreditCard, pk=pk, user=request.user)
    card.delete()
    return JsonResponse({"success": True})




@login_required
def goal_dashboard(request):

    total_emi = EMI.objects.filter(user=request.user)\
        .aggregate(total=Sum("monthly_payment"))["total"] or 0

    total_subscription = Subscription.objects.filter(user=request.user)\
        .aggregate(total=Sum("monthly_cost"))["total"] or 0

    total_spending = MonthlySpending.objects.filter(user=request.user)\
        .aggregate(total=Sum("average_monthly_amount"))["total"] or 0

    monthly_expense = total_emi + total_subscription + total_spending

    income_map = {
        "<5L": 30000,
        "5-10L": 60000,
        "10-25L": 150000,
        "25L+": 300000,
    }

    monthly_income = income_map.get(request.user.income_range, 50000)

    surplus = monthly_income - monthly_expense
    surplus = max(surplus, 0)

    warning = None

    if request.method == "POST":
        form = FinancialGoalForm(request.POST)
        if form.is_valid():

            monthly_contribution = form.cleaned_data["monthly_contribution"]

            if monthly_contribution > surplus:
                warning = "Your monthly contribution exceeds your surplus."
            else:
                goal = form.save(commit=False)
                goal.user = request.user
                goal.save()
                return redirect("goal_dashboard")
    else:
        form = FinancialGoalForm()

    goals = FinancialGoal.objects.filter(user=request.user)

    return render(
        request,
        "finance/goals.html",
        {
            "form": form,
            "goals": goals,
            "monthly_income": monthly_income,
            "monthly_expense": monthly_expense,
            "surplus": surplus,
            "warning": warning,
        }
    )




