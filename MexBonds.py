import numpy as np
import pandas as pd
from math import ceil
from Bonds import FixedPaymentsBond
from Helpers import CalendarHelper

class Cetes(FixedPaymentsBond):

    expiration = None

    def __init__(self, expiration, rate):
        super().__init__(pd.Series(expiration), pd.Series(10), rate)
        self.expiration = expiration

    def price(self, valuation_date, rate = None):
        if rate is None:
            rate = self.rate
        t = (self.expiration - valuation_date).days
        return 10 / (1+rate*t/360)


class MBonos(FixedPaymentsBond):

    expiration = None
    start_date = None
    coupon = None

    def __init__(self, expiration, rate, coupon, start_date):

        self.expiration = expiration
        self.start_date = start_date
        self.coupon = coupon

        delta = pd.Timedelta(days = 182)
        n = (expiration - start_date).days // 182
        date_list = [expiration - i*delta for i in range(n+1)]
        date_list.reverse()
        dates = pd.Series(date_list)

        coupon_payment = coupon*100*182/360
        payments = pd.Series([coupon_payment]*n + [coupon_payment+100])

        super().__init__(dates, payments, rate)

    def price(self, valuation_date=None, rate=None):

        if rate is None:
            rate = self.rate
        if valuation_date is None:
            valuation_date = self.start_date

        dates = self.payment_dates[self.payment_dates > valuation_date]
        payments = self.payments[self.payment_dates > valuation_date]

        eff_182_rate = rate*182/360
        discount_periods = CalendarHelper.day_counter(dates, valuation_date) / 182
        discount_factors = (1+eff_182_rate) ** (-discount_periods)

        return np.dot(payments, discount_factors)
    
class UDIBonos(MBonos):

    def price(self, valuation_date=None, rate=None, currency='MXN', UDI=None):
       
        udi_price = super().price(valuation_date, rate)
        
        if currency == 'UDI':
            return udi_price
        elif currency == 'MXN':
            return udi_price * UDI
        else:
            raise ValueError('Currency can only be MXN or UDI')
        