from .models import EMI, CreditCard, Subscription, MonthlySpending
from django.db.models import Sum
import math

def emi_prepayment_simulation(emi, extra_payment):

    r = emi.interest_rate / 100 / 12
    n = emi.remaining_months
    P = emi.principal_amount

    original_total_interest = (emi.monthly_payment * n) - P

    new_payment = emi.monthly_payment + extra_payment

    if r == 0:
        new_months = P / new_payment
    else:
        new_months = math.log(new_payment / (new_payment - P*r)) / math.log(1+r)

    new_months = math.ceil(new_months)

    new_total_paid = new_payment * new_months
    new_interest = new_total_paid - P

    return {
        "new_months": new_months,
        "months_saved": n - new_months,
        "interest_saved": round(original_total_interest - new_interest, 2)
    }


def debt_free_projection(user):

    emis = EMI.objects.filter(user=user)
    total_months = 0

    for emi in emis:
        if emi.remaining_months > total_months:
            total_months = emi.remaining_months

    return total_months



def estimate_cibil(user):

    cards = CreditCard.objects.filter(user=user)

    if not cards.exists():
        return 750

    avg_util = sum([c.utilization_percentage() for c in cards]) / len(cards)

    base_score = 750

    if avg_util > 75:
        base_score -= 60
    elif avg_util > 50:
        base_score -= 40
    elif avg_util > 30:
        base_score -= 20
    else:
        base_score += 10

    return max(300, min(900, base_score))




def get_income_value(user):
    income_map = {
        '<5L': 30000,
        '5-10L': 60000,
        '10-25L': 120000,
        '25L+': 250000,
    }
    return income_map.get(user.income_range, 0)


def financial_summary(user):

    monthly_income = get_income_value(user)

    emis = EMI.objects.filter(user=user)
    cards = CreditCard.objects.filter(user=user)

    total_emi = emis.aggregate(total=Sum('monthly_payment'))['total'] or 0
    total_subscriptions = Subscription.objects.filter(user=user).aggregate(
        total=Sum('monthly_cost')
    )['total'] or 0

    total_spending = MonthlySpending.objects.filter(user=user).aggregate(
        total=Sum('average_monthly_amount')
    )['total'] or 0

    total_fixed = total_emi + total_subscriptions
    total_outflow = total_fixed + total_spending
    surplus = monthly_income - total_outflow

    # -----------------------------
    # 1️⃣ EMI PREPAYMENT OPTIMIZER
    # Avalanche Strategy (highest interest first)
    # -----------------------------

    emi_optimizer = None
    if emis.exists():
        highest_interest_emi = emis.order_by('-interest_rate').first()
        interest_saved = (
            highest_interest_emi.monthly_payment *
            highest_interest_emi.remaining_months *
            (highest_interest_emi.interest_rate / 100)
        ) / 12

        months_saved = highest_interest_emi.remaining_months

        emi_optimizer = {
            "close_first": highest_interest_emi.name,
            "months_saved": months_saved,
            "interest_saved": round(interest_saved, 2)
        }

    # -----------------------------
    # 2️⃣ CREDIT UTILISATION SIMULATOR
    # -----------------------------

    credit_simulation = []
    for card in cards:
        utilization = card.utilization_percentage()

        # Estimated CIBIL impact logic
        if utilization > 75:
            score_impact = -40
        elif utilization > 50:
            score_impact = -20
        elif utilization > 30:
            score_impact = -5
        else:
            score_impact = +10

        optimal_payment = max(
            (card.total_limit * 0.3) - (card.total_limit - card.available_limit),
            0
        )

        credit_simulation.append({
            "card": card.bank_name,
            "utilization": round(utilization, 1),
            "cibil_impact": score_impact,
            "optimal_payment": round(optimal_payment, 2)
        })

    # -----------------------------
    # 3️⃣ CASHFLOW RISK SCORE
    # -----------------------------

    if monthly_income == 0:
        risk_level = "Unknown"
        liquidity_probability = 0
    else:
        debt_ratio = total_emi / monthly_income

        if surplus < monthly_income * 0.1:
            risk_level = "High"
            liquidity_probability = 70
        elif debt_ratio > 0.5:
            risk_level = "High"
            liquidity_probability = 65
        elif debt_ratio > 0.35:
            risk_level = "Medium"
            liquidity_probability = 35
        else:
            risk_level = "Low"
            liquidity_probability = 15

    # -----------------------------
    # 4️⃣ SMART ALERTS
    # -----------------------------

    alerts = []

    if surplus < monthly_income * 0.1:
        alerts.append("⚠ Surplus below 10% of income.")

    if total_emi > monthly_income * 0.5:
        alerts.append("🚨 EMI exceeds 50% of income.")

    if risk_level == "High":
        alerts.append("High liquidity risk detected.")

    return {
        "monthly_income": monthly_income,
        "total_emi": total_emi,
        "subscriptions": total_subscriptions,
        "spending": total_spending,
        "surplus": surplus,
        "emi_optimizer": emi_optimizer,
        "credit_simulation": credit_simulation,
        "risk_level": risk_level,
        "liquidity_probability": liquidity_probability,
        "alerts": alerts
    }
