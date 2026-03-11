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
from .goal_engine import GoalEngine
from .planner_engine import MicroPlannerEngine


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

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "card":
            card_form = CreditCardForm(request.POST)
            if card_form.is_valid():
                card = card_form.save(commit=False)
                card.user = request.user
                card.save()
                return redirect("transactions")

        elif form_type == "emi":
            emi_form = EMIForm(request.POST)
            if emi_form.is_valid():
                emi = emi_form.save(commit=False)
                emi.user = request.user
                emi.save()
                return redirect("transactions")

        elif form_type == "sub":
            sub_form = SubscriptionForm(request.POST)
            if sub_form.is_valid():
                sub = sub_form.save(commit=False)
                sub.user = request.user
                sub.save()
                return redirect("transactions")

        elif form_type == "spend":
            spend_form = SpendingForm(request.POST)
            if spend_form.is_valid():
                spend = spend_form.save(commit=False)
                spend.user = request.user
                spend.save()
                return redirect("transactions")

    else:
        card_form = CreditCardForm()
        emi_form = EMIForm()
        sub_form = SubscriptionForm()
        spend_form = SpendingForm()

    # Pagination
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
        "card_form": card_form,
        "emi_form": emi_form,
        "sub_form": sub_form,
        "spend_form": spend_form,
        "page_obj": page_obj,
        "emis": emis,
        "subs": subs,
        "spendings": spendings,
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

    warning = None

    if request.method == "POST":
        form = FinancialGoalForm(request.POST)

        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user

            engine = GoalEngine(
                goal.target_amount,
                goal.current_amount,
                goal.expected_annual_return
            )

            # If user selected target_date
            if goal.target_date:
                months = (
                    (goal.target_date.year - date.today().year) * 12
                    + (goal.target_date.month - date.today().month)
                )

                goal.monthly_contribution = engine.required_monthly_for_timeline(months)

            # If user entered monthly contribution only
            elif goal.monthly_contribution:
                months = engine.months_required(goal.monthly_contribution)

                if months:
                    goal.target_date = date.today().replace(
                        year=date.today().year + int(months // 12)
                    )

            goal.save()
            return redirect("goal_dashboard")
    else:
        form = FinancialGoalForm()

    goals = FinancialGoal.objects.filter(user=request.user)

    # Add computed values
    enriched_goals = []

    for goal in goals:

        years = 5  # Or calculate from target_date

        engine = MicroPlannerEngine(
            goal.target_amount,
            goal.current_amount,
            goal.monthly_contribution or 0,
            goal.expected_annual_return,
            years
        )

        projection = engine.projected_value()
        monte = engine.monte_carlo()

        health = engine.health_score(monte["success_rate"])

        enriched_goals.append({
            "goal": goal,
            "projection": projection,
            "monte": monte,
            "health": health,
        })

    return render(
        request,
        "finance/goals.html",
        {
            "form": form,
            "goals": enriched_goals,
            "warning": warning,
        }
    )