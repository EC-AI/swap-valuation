import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import BDay

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
    
    def constant_hazard_rate(self):
        return 0.014602921
    
    @staticmethod
    def survival_p(hazard_rate, dates, start_date):
        days = np.array((pd.Series(dates) - start_date).dt.days)
        return np.exp(-hazard_rate * days/365)

    def __init__(self, notional, traded_spread, start_date, end_date, cash_date, coupon=100):
        self.notional = notional
        self.traded_spread = traded_spread
        self.start_date = start_date
        self.cash_date = cash_date
        self.end_date = end_date
        self.coupon = coupon
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

    def cash_amount(self, discount_curve):
        if not isinstance(discount_curve, DiscountCurve):
            raise ValueError('discount_curve must be instance of DiscountCurve class')
        survival_probabilities = CDS.survival_p(self.constant_hazard_rate(), self.coupon_dates, self.start_date)
        return discount_curve.pv(self.coupon_dates, (self.theoretic_payments-self.payments)*survival_probabilities, self.cash_date)
        #return discount_curve.pv(self.coupon_dates, self.theoretic_payments, self.cash_date) - discount_curve.pv(self.coupon_dates, self.payments, self.cash_date)

    def to_pandas(self, discount_curve):
        if not isinstance(discount_curve, DiscountCurve):
            raise ValueError('discount_curve must be instance of DiscountCurve class')
        return pd.DataFrame(data={
            'Date': self.coupon_dates.values,
            'Act. Cashflow': self.payments.values,
            'Discount Factor': discount_curve.discount_factor(self.coupon_dates, self.cash_date)
        })

    def __str__(self):
        return str(self.to_pandas())