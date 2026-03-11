import random
import statistics
from decimal import Decimal
from datetime import date
import math


class MicroPlannerEngine:

    def __init__(self, target, current, monthly, annual_return, years):
        self.target = Decimal(target)
        self.current = Decimal(current)
        self.monthly = Decimal(monthly)
        self.annual_return = float(annual_return)
        self.years = years
        self.months = years * 12

    # ─────────────────────────────
    # Deterministic projection
    # ─────────────────────────────
    def projected_value(self):
        r = self.annual_return / 100 / 12
        value = float(self.current)

        for _ in range(self.months):
            value = value * (1 + r) + float(self.monthly)

        return Decimal(value)

    # ─────────────────────────────
    # Monte Carlo Simulation
    # ─────────────────────────────
    def monte_carlo(self, simulations=500):

        results = []

        for _ in range(simulations):
            value = float(self.current)

            for _ in range(self.months):
                random_return = random.gauss(
                    self.annual_return / 100 / 12,
                    0.02   # volatility assumption (2% monthly)
                )
                value = value * (1 + random_return) + float(self.monthly)

            results.append(value)

        success_rate = sum(1 for r in results if r >= float(self.target)) / simulations
        median_value = statistics.median(results)

        return {
            "success_rate": round(success_rate * 100, 2),
            "median_value": round(median_value, 2),
            "worst_case": round(min(results), 2),
            "best_case": round(max(results), 2),
        }

    # ─────────────────────────────
    # Goal Health Score
    # ─────────────────────────────
    def health_score(self, success_rate):

        if success_rate >= 80:
            return 90
        elif success_rate >= 60:
            return 75
        elif success_rate >= 40:
            return 55
        else:
            return 30