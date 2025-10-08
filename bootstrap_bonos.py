import pandas as pd
from MexBonds import Cetes, MBonos
from Bootstrap import Bootstrap
import numpy as np

bonos = pd.read_excel('prueba_bootstrap_bonos.xlsx', 'Bonos y Cetes')

fecha = pd.Timestamp('20240214')
lista_bonos = []
precios = []
# fechas = [fecha]
# tasas = [bonos['Tasa'].iloc[0]]
fechas = []
tasas = []

for i in range(len(bonos)):
    fechas.append(bonos['Vencimiento'].iloc[i])
    tasas.append(bonos['Tasa'].iloc[i])
    if bonos['Tipo valor'].iloc[i] == 'BI' or bonos['Tipo valor'].iloc[i] == 'RC':
        lista_bonos.append(Cetes(bonos['Vencimiento'].iloc[i], bonos['Tasa'].iloc[i]))
    elif bonos['Tipo valor'].iloc[i] == 'M':
        lista_bonos.append(MBonos(bonos['Vencimiento'].iloc[i], bonos['Tasa'].iloc[i], bonos['Cupon'].iloc[i], fecha))
    else:
        raise ValueError('Bond type not recognized')

for i in range(len(bonos)):
    precios.append(lista_bonos[i].price(fecha))

bootstrap = Bootstrap(lista_bonos, precios, fechas, fecha)
bootstrap.fit(np.array(tasas))

print(bootstrap.result)
c = Cetes(pd.Timestamp("20240222"), 0.1123)
print(c.curve_valuation(bootstrap.dc, pd.Timestamp("20240214")))
print(c.price(pd.Timestamp("20240214")))

bootstrap.result.to_pandas().to_excel('bootstrap_result.xlsx', sheet_name='Bonos y Cetes')