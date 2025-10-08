import pandas as pd
from scipy.optimize import minimize
from DiscountCurve import DiscountCurve

class FixedPaymentsBond():

    payment_dates = None
    payments = None
    rate = None

    def __init__(self, payment_dates, payments, rate):
        self.payment_dates = payment_dates
        self.payments = payments
        self.rate = rate

    def curve_valuation(self, discount_curve, valuation_date):

        if not isinstance(discount_curve, DiscountCurve):
            raise ValueError('discount_curve must be instance of DiscountCurve class')
        
        dates = self.payment_dates[self.payment_dates > valuation_date]
        payments = self.payments[self.payment_dates > valuation_date]

        return discount_curve.pv(dates, payments, valuation_date)

    def set_price(self, price, valuation_date, tol=1e-10):
        res = minimize(lambda r: (self.price(valuation_date, r) - price)**2, self.rate, method='BFGS')
        self.rate = res.x[0]
        return self.rate

    def price(self, valuation_date, rate=None):
        raise NotImplementedError
    
    def payment_calendar(self):
        return pd.DataFrame(data={
            'Date': self.payment_dates.values,
            'Payment': self.payments.values,
        })
    
    def dv01(self, valuation_date=None, rate=None):
        if rate is None:
            rate = self.rate
        if valuation_date is None:
            valuation_date = self.start_date
        rate_plus = rate + 0.0001
        rate_minus = rate - 0.0001
        p_plus = self.price(valuation_date, rate_plus)
        p_minus = self.price(valuation_date, rate_minus)
        return (p_minus - p_plus) / 2