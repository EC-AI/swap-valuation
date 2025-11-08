import numpy as np
import pandas as pd
from CDS import CDS
from pandas.tseries.offsets import BDay

from DiscountCurve import DiscountCurve

cds = CDS(10000000, traded_spread=92, start_date=pd.Timestamp('20251024'), end_date=pd.Timestamp('20301220'), cash_date=pd.Timestamp('20251029'))

zc = pd.read_excel('curvas2.xlsx', 'Curva')

zc['ZR'] = zc['ZR']/100
dc = DiscountCurve(zc['Fecha'], zc['ZR'], pd.Timestamp('20251024'))
#print(cds.coupon_dates)
#print(dc.discount_factor(cds.coupon_dates, pd.Timestamp('20251024')))
print(cds.find_constant_hazard_rate(dc))
print(cds.cash_amount(dc))
#print(cds.premium_leg_pv(dc))
#print(cds.protection_leg_pv(dc, hazard_rate=-0.0124447474190746))
#print(cds.to_pandas(dc))
#print(cds.coupon_dates)


from MexBonds import Cetes, MBonos

# c = Cetes(pd.Timestamp('20230427'), 0.1127)
# print(c.payment_calendar())
# print(c.price(pd.Timestamp('20230410')))

# dc = DiscountCurve(
#     pd.Series([pd.Timestamp('20230410'), pd.Timestamp('20230430')]), 
#     pd.Series([0.11390905012499783, 0.11390905012499783]), 
#     pd.Timestamp('20230410'))

# print(c.curve_valuation(dc, pd.Timestamp('20230410')))

# c.set_price(9.9, pd.Timestamp('20230410'))

# print(c.rate)


# m = MBonos(pd.Timestamp('20311127'), .044, .0275, pd.Timestamp('20230413'))
# # print(m.payment_calendar())
# print(m.set_price(88.96367, valuation_date=pd.Timestamp('20230413')))
# print(m.price())