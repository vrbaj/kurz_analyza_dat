import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# načtení data
df = pd.read_csv('sampanske.csv')
# hlavička
print(df.head())
# velikost tabulky
print(df.shape)
# konec tabulky
print(df.tail())
# smazání NaN řádků
df.dropna(inplace=True)
# kontrola velikosti tabulky a konce
print(df.shape)
print(df.tail())
# kontrola datovýc typů
print(df.info())
# základní stat. přehled
print(df.describe())
# převedení informaci o měsíci a roce na datetime
df["mesic"] = pd.to_datetime(df["mesic"])
# vykreslení časové řady
df["prodano"].plot()

# 1. krok analýzy časových řad - zjištění stacionarity
test_result = adfuller(df["prodano"])
print(test_result)
if test_result[1] < 0.05:
    print("časová řada je stacionární")
else:
    print("Nestacionární časová řada")

fig = plt.figure(figsize=(12, 8))
ax1 = fig.add_subplot(211)
fig = plot_acf(df["prodano"], lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = plot_pacf(df["prodano"], lags=40, ax=ax2)

# když není stacionární tak musíme diferncovat
df["prodano diference"] = df["prodano"] - df["prodano"].shift(1)
print(df["prodano diference"])
# je diferencovaná řada stacionární?
test_result = adfuller(df["prodano diference"].dropna())
print(test_result)
if test_result[1] < 0.05:
    print("časová řada je stacionární pro dif1")
else:
    print("Nestacionární časová řada dif1")

df["prodano diference"] = df["prodano"] - df["prodano"].shift(12)
print(df.head(20))
# je diferencovaná řada stacionární?
test_result = adfuller(df["prodano diference"].dropna())
print(test_result)
if test_result[1] < 0.05:
    print("časová řada je stacionární pro dif12")
else:
    print("Nestacionární časová řada dif12")
# vykreslení dif. časové řado (12)
fig = plt.figure()
plt.title("Dif 12 časová řada")
fig = df["prodano diference"].plot()

# vykreslení autokorelační a parciální autokorelační funkce
fig = plt.figure()
ax1 = fig.add_subplot(211)
fig = plot_acf(df["prodano diference"].iloc[13:], lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = plot_pacf(df["prodano diference"].iloc[13:], lags=40, ax=ax2)

# AR model
model = ARIMA(df["prodano"][:90], order=(1, 1, 1))
model_fit = model.fit()
print(model_fit.summary())
# predikce modelu
df["predikce"] = model_fit.predict(start=90, end=103, dynamic=True)
# vykreslení predikce modelu
plt.figure()
df[["prodano", "predikce"]].plot()
# analýza chyb predikce (residuí)
residua = pd.DataFrame(model_fit.resid)
plt.figure()
residua.plot()
plt.title("Residua")
plt.figure()
residua.plot(kind="kde")
print(residua.describe())
# sezónní ARIMA model
model = sm.tsa.statespace.SARIMAX(df["prodano"][:90], order=(1, 1, 1),
                             seasonal_order=(1, 1, 1, 12))
sarimax_fit = model.fit()
print(sarimax_fit.summary())
sarimax_fit.plot_diagnostics()

df["sarimax_predikce"] = sarimax_fit.predict(start=90, end=103, dynamic=True)
plt.figure()
df[["prodano", "sarimax_predikce"]].plot()
plt.show()