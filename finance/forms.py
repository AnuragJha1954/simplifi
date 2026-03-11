from django import forms
from .models import CreditCard, EMI, Subscription, MonthlySpending, FinancialGoal


class BaseStyledForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():

            # Toggle styling separately
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    "class": "toggle-checkbox hidden"
                })
            else:
                field.widget.attrs.update({
                    "class": "w-full h-14 px-5 rounded-xl border border-slate-300 "
                             "bg-white text-slate-800 placeholder-slate-400 "
                             "focus:outline-none focus:ring-4 focus:ring-cyan-100 "
                             "focus:border-cyan-500 transition text-base",
                })

            field.label = ""


class CreditCardForm(BaseStyledForm):
    class Meta:
        model = CreditCard
        fields = ['bank_name', 'total_limit', 'available_limit', 'interest_rate']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['bank_name'].widget.attrs['placeholder'] = "Bank Name (e.g., HDFC, ICICI)"
        self.fields['total_limit'].widget.attrs['placeholder'] = "Total Credit Limit (₹)"
        self.fields['available_limit'].widget.attrs['placeholder'] = "Available Credit (₹)"
        self.fields['interest_rate'].widget.attrs['placeholder'] = "Annual Interest Rate (%) e.g. 36"

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get("total_limit")
        available = cleaned_data.get("available_limit")

        if total and available and available > total:
            raise forms.ValidationError(
                "Available limit cannot exceed total credit limit."
            )

        return cleaned_data


class EMIForm(BaseStyledForm):
    class Meta:
        model = EMI
        fields = ['name', 'principal_amount', 'monthly_payment',
                  'interest_rate', 'remaining_months']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['placeholder'] = "EMI Name (e.g., Car Loan)"
        self.fields['principal_amount'].widget.attrs['placeholder'] = "Principal Amount (₹)"
        self.fields['monthly_payment'].widget.attrs['placeholder'] = "Monthly EMI Amount (₹)"
        self.fields['interest_rate'].widget.attrs['placeholder'] = "Annual Interest Rate (%)"
        self.fields['remaining_months'].widget.attrs['placeholder'] = "Remaining Months"


class SubscriptionForm(BaseStyledForm):
    class Meta:
        model = Subscription
        fields = ['name', 'monthly_cost', 'is_essential']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['placeholder'] = "Subscription Name (e.g., Netflix)"
        self.fields['monthly_cost'].widget.attrs['placeholder'] = "Monthly Cost (₹)"


class SpendingForm(BaseStyledForm):
    class Meta:
        model = MonthlySpending
        fields = ['category', 'average_monthly_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].widget.attrs['placeholder'] = "Spending Category (e.g., Groceries)"
        self.fields['average_monthly_amount'].widget.attrs['placeholder'] = "Average Monthly Spending (₹)"




class FinancialGoalForm(forms.ModelForm):

    class Meta:
        model = FinancialGoal
        fields = [
            "goal_type",
            "name",
            "target_amount",
            "current_amount",
            "target_date",
            "monthly_contribution",
            "expected_annual_return",
        ]