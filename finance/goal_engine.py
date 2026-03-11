# finance/services/goal_engine.py

from datetime import date
from decimal import Decimal
import math


class GoalEngine:

    def __init__(self, target, current, annual_return):
        self.target = Decimal(target)
        self.current = Decimal(current)
        self.r = Decimal(annual_return) / Decimal(100) / Decimal(12)

    def remaining_amount(self):
        return max(self.target - self.current, Decimal(0))

    # Case 1 — Calculate required SIP for a target date
    def required_monthly_for_timeline(self, months):
        if months <= 0:
            return Decimal(0)

        FV = self.remaining_amount()

        if self.r == 0:
            return FV / months

        sip = FV * self.r / ((1 + self.r) ** months - 1)
        return sip

    # Case 2 — Calculate months required if monthly contribution is fixed
    def months_required(self, monthly):
        if monthly <= 0:
            return None

        FV = self.remaining_amount()

        if self.r == 0:
            return FV / monthly

        numerator = math.log(
            float((monthly + FV * self.r) / monthly)
        )
        denominator = math.log(float(1 + self.r))

        return numerator / denominator

    def progress_percent(self):
        if self.target == 0:
            return 0
        return (self.current / self.target) * 100