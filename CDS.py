import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import BDay
from scipy.optimize import newton

from DiscountCurve import DiscountCurve

class CDS():

    def _coupon_dates(self):
        months = [3, 6, 9, 12]
        dates = pd.Series([pd.Timestamp(month=12, day=20, year=self.start_date.year - 1)] 
         + [pd.Timestamp(day=20, month=m, year=y) for y in range(self.start_date.year, self.end_date.year+1) for m in months])
        adj_dates = dates + 0*BDay()
        return np.max(adj_dates[adj_dates <= self.start_date]), adj_dates[(adj_dates > self.start_date) & (adj_dates <= self.end_date)]

    def _act_360_counter(self, dates):
        return (dates-dates.shift(1)).dt.days.iloc[1:]/360

    @staticmethod
    def survival_p(hazard_rate, dates, start_date):
        days = np.array((pd.Series(dates) - start_date).dt.days)
        return np.exp(-hazard_rate * days/365)

    @staticmethod
    def _discounted_contingent_payments(dates, payments, valuation_date, discount_curve, hazard_rate, start_date=None):
        if start_date is None:
            start_date = valuation_date
        survival_probabilities = CDS.survival_p(hazard_rate, dates, start_date)
        return discount_curve.pv(dates, payments*survival_probabilities, valuation_date)
    
    @staticmethod
    def _protection_pv_integral(notional, start_date, dates, discount_curve, hazard_rate, recovery_rate):
        LGD = 1 - recovery_rate
        dates = pd.concat((pd.Series(start_date), dates))
        discount_factors = discount_curve.discount_factor(dates, start_date)
        survival_probabilities = CDS.survival_p(hazard_rate, dates, start_date)
        timedelta = (dates - dates.shift(1)).dt.days.values[1:]/365
        log_df = np.log(discount_factors)
        effective_forwards = log_df[:-1] - log_df[1:]
        forwards = effective_forwards / timedelta
        hazard_forward = (forwards + hazard_rate) 
        return LGD * notional * hazard_rate * np.sum(discount_factors[:-1] * survival_probabilities[:-1] * (1 - np.exp(-hazard_forward * timedelta)) / hazard_forward)


    def __init__(self, notional, traded_spread, start_date, end_date, cash_date, coupon=100, recovery_rate=0.25):
        self.notional = notional
        self.traded_spread = traded_spread
        self.start_date = start_date
        self.cash_date = cash_date
        self.end_date = end_date
        self.coupon = coupon
        self.recovery_rate = recovery_rate
        self.previous_date, self.coupon_dates = self._coupon_dates()
        if not self.end_date == self.coupon_dates.iloc[-1]:
            raise ValueError('Invalid end date')
        self.payment_factors = pd.concat((
            self._act_360_counter(pd.Series([self.previous_date, self.coupon_dates.iloc[0]])), 
            self._act_360_counter(self.coupon_dates)
        ), ignore_index=True)
        self.payments = self.payment_factors * (self.notional*self.coupon/10000)
        self.theoretic_payments = self.payment_factors * (self.notional*self.traded_spread/10000)
        self.theoretic_payments.iloc[0] = self._act_360_counter(pd.Series([self.start_date, self.coupon_dates.iloc[0]])) * (self.notional*self.traded_spread/10000)

    def find_constant_hazard_rate(self, discount_curve):
        def objective(hazard_rate):
            return CDS._discounted_contingent_payments(self.coupon_dates, self.theoretic_payments, self.start_date, discount_curve, hazard_rate) - CDS._protection_pv_integral(self.notional, self.start_date, self.coupon_dates, discount_curve, hazard_rate, self.recovery_rate)
        res = newton(objective, .01)
        return res

    def premium_leg_pv(self, discount_curve, hazard_rate=None, date=None, payments="Theoretical"):
        if not isinstance(discount_curve, DiscountCurve):
            raise ValueError('discount_curve must be instance of DiscountCurve class')
        
        switcher = {
            "Theoretical": self.theoretic_payments,
            "Actual": self.payments
        }
        payments = switcher.get(payments)
        if payments is None:
            raise ValueError('payments must be "Theoretical" or "Actual"')

        if date is None:
            date = self.start_date

        # Get the constant hazard rate that is consistent with traded spread
        if hazard_rate is None:
            hazard_rate = self.find_constant_hazard_rate(discount_curve)

        return CDS._discounted_contingent_payments(self.coupon_dates, payments, date, discount_curve, hazard_rate, self.start_date)
    
    def protection_leg_pv(self, discount_curve, hazard_rate=None):
        if not isinstance(discount_curve, DiscountCurve):
            raise ValueError('discount_curve must be instance of DiscountCurve class')

        # Get the constant hazard rate that is consistent with traded spread
        if hazard_rate is None:
            hazard_rate = self.find_constant_hazard_rate(discount_curve)

        return CDS._protection_pv_integral(self.notional, self.start_date, self.coupon_dates, discount_curve, hazard_rate, self.recovery_rate)

    def cash_amount(self, discount_curve):
        if not isinstance(discount_curve, DiscountCurve):
            raise ValueError('discount_curve must be instance of DiscountCurve class')
        
        hazard_rate = self.find_constant_hazard_rate(discount_curve)
        theoretic = self.premium_leg_pv(discount_curve, hazard_rate=hazard_rate, payments="Theoretical")
        actual = self.premium_leg_pv(discount_curve, hazard_rate=hazard_rate, payments="Actual")        
        return theoretic - actual

    def to_pandas(self, discount_curve):
        if not isinstance(discount_curve, DiscountCurve):
            raise ValueError('discount_curve must be instance of DiscountCurve class')
        return pd.DataFrame(data={
            'Date': self.coupon_dates.values,
            'Act. Cashflow': self.payments.values,
            'Discount Factor': discount_curve.discount_factor(self.coupon_dates, self.cash_date),
            'Discount Factor': discount_curve.discount_factor(self.coupon_dates, self.cash_date),
            'Survival Probability': CDS.survival_p(self.find_constant_hazard_rate(discount_curve), self.coupon_dates.values, self.start_date)
        })

    def __str__(self):
        return str(self.to_pandas())