import numpy as np
import pandas as pd

class CalendarHelper():

    @staticmethod
    def day_counter(dates, start_date):
        return np.array((pd.Series(dates) - start_date).dt.days)
