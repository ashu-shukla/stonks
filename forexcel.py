import pandas as pd
from nsepy import get_history
from datetime import date
data = get_history(symbol="NIFTY", start=date(
    2017, 1, 1), end=date(2022, 8, 30), index=True)
data.to_csv('data.csv')
