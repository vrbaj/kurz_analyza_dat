import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1) nahrání souboru s daty
df_raw = pd.read_excel("inputs/auto_cr.xlsx")

print(df_raw.head())