import numpy as np
import pandas as pd
from DiscountCurve import DiscountCurve
from scipy.optimize import minimize

class Bootstrap():

    result = None

    def __init__(self, security_list, market_values, discount_curve_dates, valuation_date):
        self.security_list = security_list
        self.market_values = np.array(market_values)
        self.discount_curve_dates = np.array(discount_curve_dates)
        self.valuation_date = valuation_date

    def loss_function(self, zero_rates):
        self.dc.set_rates(zero_rates)
        valuation_result = np.array(list(map(lambda sec: sec.curve_valuation(self.dc, self.valuation_date), self.security_list)))
        return np.sum((valuation_result - self.market_values) ** 2)
    
    def fit(self, initial_zero_rates=None):
        if initial_zero_rates is None:
            initial_zero_rates = np.zeros(len(self.discount_curve_dates))
        self.dc = DiscountCurve(self.discount_curve_dates, initial_zero_rates, self.valuation_date)
        res = minimize(lambda rates: self.loss_function(rates), initial_zero_rates, method='Nelder-Mead')
        self.result = DiscountCurve(self.discount_curve_dates, res.x, self.valuation_date)
