import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

class DiscountCurve():

    def _dates_to_relative(self, dates):
        return np.array((pd.Series(dates) - self.valuation_date).dt.days)

    def __init__(self, curve_dates, zero_rates, valuation_date, interpolation_kind='linear'):
        self.curve_dates = np.array(curve_dates)
        self.zero_rates = np.array(zero_rates)
        self.valuation_date = valuation_date
        self.relative_dates = self._dates_to_relative(curve_dates)
        self.rel_interpolator = interp1d(self.relative_dates, zero_rates, kind=interpolation_kind)
        self.interpolation_kind = interpolation_kind

    def set_rates(self, rates):
        self.zero_rates = np.array(rates)
        self.rel_interpolator = interp1d(self.relative_dates, self.zero_rates, kind=self.interpolation_kind)

    def interpolate_zr(self, dates):
        rel_dates = self._dates_to_relative(dates)
        return self.rel_interpolator(rel_dates)

    def discount_factor(self, dates, pv_date = None):

        if pv_date is not None and pv_date < self.valuation_date:
            raise ValueError('pv_date can\'t be prior to curve valuation date')

        zr = self.interpolate_zr(dates)
        days = self._dates_to_relative(dates)

        # If pv_date is None, we compute PV as of self.valuation_date and no adjustment is necessary
        if pv_date is None or pv_date == self.valuation_date:
            pv_date_adjustment = 0
        else:
            pv_date_zr = self.interpolate_zr(pv_date)
            days_pv = self._dates_to_relative(pv_date)
            pv_date_adjustment = pv_date_zr*days_pv/365

        return np.exp(-zr*days/365 + pv_date_adjustment)

    def pv(self, payment_dates, payments, pv_date = None):
        df = self.discount_factor(payment_dates, pv_date)
        return np.dot(df, payments)
    
    def effective_forward_rates(self, from_dates, to_dates):
        from_df = self.discount_factor(from_dates)
        to_df = self.discount_factor(to_dates)
        return (from_df / to_df) - 1

    def to_pandas(self):
        return pd.DataFrame(data={'Zero Rate': np.array(self.zero_rates)}, index=np.array(self.curve_dates))

    def __repr__(self):
        return self.to_pandas().to_string()
