import numpy as np
import pandas as pd
from CDS import CDS
from pandas.tseries.offsets import BDay

from DiscountCurve import DiscountCurve

cds = CDS(10000000, traded_spread=103, start_date=pd.Timestamp('20230909'), end_date=pd.Timestamp('20280620'), cash_date=pd.Timestamp('20230911'))

zc = pd.read_excel('curvas2.xlsx', 'Curva')

zc['ZR'] = zc['ZR']/100
dc = DiscountCurve(zc['Fecha'], zc['ZR'], pd.Timestamp('20230909'))
print(dc.discount_factor(cds.coupon_dates, pd.Timestamp('20230910')))
#print(cds.cash_amount(dc))
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