import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import dateparser
import warnings
from tqdm.contrib.itertools import product
from sklearn.metrics import root_mean_squared_error as rmse

def hledani_arima(trenovaci, testovaci, p, q, sezonnost=(0, 0, 0, 0),
                  exogenni_trenovaci=None, exogenni_testovaci=None):
    """
    prohledá všechny kombinace od 0 až do p a od 0 až do q a najde nejlepší
    ARIMA model, s tím že kvalitu posoudíme podle RMSE
    """
    nejlepsi_vysledek = {
        "rmse": 10e60,
        "predikce": [],
        "model": "",
        "p": 0,
        "q": 0,
        "d": 0,
        "sezonnost": sezonnost
    }
    for p_hodnota, d_hodnota, q_hodnota in product(range(p + 1),
                                                   range(5),
                                                   range(q + 1)):
        if sezonnost[3] != 0:
            if p_hodnota >= sezonnost[3] or q_hodnota >= sezonnost[3]:
                continue
        try:
            model = ARIMA(trenovaci, order=(p_hodnota, d_hodnota, q_hodnota),
                          seasonal_order=sezonnost,
                          trend="n", exog=exogenni_trenovaci)
        except Exception as ex:
            print(ex)
            print(p_hodnota, d_hodnota, q_hodnota, sezonnost)
            raise
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            try:
                # nalezení parametrů modelu
                model_fit = model.fit()
                # predikce modelu
                predikce = model_fit.predict(start=min(testovaci.index),
                                             end=max(testovaci.index), dynamic=True,
                                             exog=exogenni_testovaci)
                rmse_hodnota = rmse(testovaci, predikce)
                if rmse_hodnota < nejlepsi_vysledek["rmse"]:
                    nejlepsi_vysledek["rmse"] = rmse_hodnota
                    nejlepsi_vysledek["predikce"] = predikce
                    nejlepsi_vysledek["model"] = (f"ARMA p={p_hodnota}, "
                                                  f"q={q_hodnota}, "
                                                  f"d={d_hodnota},"
                                                  f"sezonnost={sezonnost}")
                    nejlepsi_vysledek["p"] = p_hodnota
                    nejlepsi_vysledek["q"] = q_hodnota
                    nejlepsi_vysledek["d"] = d_hodnota
            except:
                pass
    return nejlepsi_vysledek
# reprodukovatelnost
np.random.seed(42)
# načteme tabulku dat
data = pd.read_excel("vyvoj_cen_jidlo_upraveno.xlsx")
data.set_index("datum", inplace=True)
# hlavička tabulky
print("HLAVIČKA TABULKY")
print(data.head())
# konec hlavičky
print("KONEC TABULKY")
print(data.tail())
# změna datumu na datum
data.reset_index(inplace=True)
data["datum"] = data["datum"].apply(lambda x: dateparser.parse(x))
print(data.head())
# převedení na datetime
data["datum"] = pd.to_datetime(data["datum"])
# setřídění dat od nejstarších po nejnovější
data.sort_values(by="datum", inplace=True)
print(data.head())
# z datumu uděláme index
data.set_index("datum", inplace=True)
print(data.head())
# velikost tabulky
print(data.shape)
# odstranění nečíselných hodnot
data.dropna(inplace=True)
print(data.shape)
# přehled průměrných hodnot, outlierů, atp.
print(data.describe())
# přehled sloupců
print(data.columns)
# vykreslení časové řady
data["Vepřová pečeně [1 kg]"].plot()

# nastavení frekvence indexu
data.index = pd.DatetimeIndex(data.index).to_period("M")
# připrava dat na trénvací a testovací
trenovaci_velikost = int(len(data["Vepřová pečeně [1 kg]"]) * 0.9)
trenovaci_data = data["Vepřová pečeně [1 kg]"][:trenovaci_velikost]
testovaci_data = data["Vepřová pečeně [1 kg]"][trenovaci_velikost:]
# kontrola ACF a PACF
plt.figure()
plt.subplot(121)
plot_acf(trenovaci_data, ax=plt.gca(), lags=26)
plt.title("ACF")
plt.subplot(122)
plot_pacf(trenovaci_data, ax=plt.gca(), lags=26)
plt.title("PACF")
# ověření stacionarity
stacionarita = adfuller(trenovaci_data)
print(f"p-hodnota z ADF: {stacionarita[1]}")
if stacionarita[1] < 0.05:
    print("Řada je stacionární")
else:
    print("Řada není stacionární")


plt.show()

# ar_vysledek = hledani_arima(trenovaci_data, testovaci_data, p=13, q=0, sezonnost=(0, 0, 0, 0))
# ma_vysledek =  hledani_arima(trenovaci_data, testovaci_data, p=0, q=13, sezonnost=(0, 0, 0, 0))
# arma_vysledek = hledani_arima(trenovaci_data, testovaci_data, p=9, q=9, sezonnost=(0, 0, 0, 0))
# ar_vysledek_sez = hledani_arima(trenovaci_data, testovaci_data, p=13, q=0, sezonnost=(1, 1, 1, 12))
# ma_vysledek_sez =  hledani_arima(trenovaci_data, testovaci_data, p=0, q=20, sezonnost=(1, 1, 1, 12))
# arma_vysledek_sez = hledani_arima(trenovaci_data, testovaci_data, p=9, q=9, sezonnost=(1, 1, 1, 12))
#
# import pickle
# with open("arma.pk", "wb") as f:
#     pickle.dump([ar_vysledek, ma_vysledek, arma_vysledek, ar_vysledek_sez,
#                ma_vysledek_sez, arma_vysledek_sez], f)

# ARX, ARMAX, MAX,...
# příprava exogenních prom.
trenovaci_exo1 = data["Vepřová kýta bez kosti [1 kg]"][:trenovaci_velikost]
testovaci_exo1 = data["Vepřová kýta bez kosti [1 kg]"][trenovaci_velikost:]
trenovaci_exo2 = data["Vepřová krkovice [1 kg]"][:trenovaci_velikost]
testovaci_exo2 = data[("Vepřová krkovice [1 kg]")][trenovaci_velikost:]
exog_trenovaci_pd = pd.DataFrame({"Vepřová kýta bez kosti [1 kg]": trenovaci_exo1,
                                 "Vepřová krkovice [1 kg]": trenovaci_exo2})
exog_testovaci_pd = pd.DataFrame({"Vepřová kýta bez kosti [1 kg]": testovaci_exo1,
                                 "Vepřová krkovice [1 kg]": testovaci_exo2})

ar_vysledek = hledani_arima(trenovaci_data, testovaci_data, p=13, q=0, sezonnost=(0, 0, 0, 0),
                            exogenni_trenovaci=exog_trenovaci_pd,
                            exogenni_testovaci=exog_testovaci_pd)
ma_vysledek =  hledani_arima(trenovaci_data, testovaci_data, p=0, q=13, sezonnost=(0, 0, 0, 0),
                            exogenni_trenovaci=exog_trenovaci_pd,
                            exogenni_testovaci=exog_testovaci_pd)
arma_vysledek = hledani_arima(trenovaci_data, testovaci_data, p=9, q=9, sezonnost=(0, 0, 0, 0),
                            exogenni_trenovaci=exog_trenovaci_pd,
                            exogenni_testovaci=exog_testovaci_pd)
ar_vysledek_sez = hledani_arima(trenovaci_data, testovaci_data, p=13, q=0, sezonnost=(1, 1, 1, 12),
                            exogenni_trenovaci=exog_trenovaci_pd,
                            exogenni_testovaci=exog_testovaci_pd)
ma_vysledek_sez =  hledani_arima(trenovaci_data, testovaci_data, p=0, q=20, sezonnost=(1, 1, 1, 12),
                            exogenni_trenovaci=exog_trenovaci_pd,
                            exogenni_testovaci=exog_testovaci_pd)
arma_vysledek_sez = hledani_arima(trenovaci_data, testovaci_data, p=9, q=9, sezonnost=(1, 1, 1, 12),
                            exogenni_trenovaci=exog_trenovaci_pd,
                            exogenni_testovaci=exog_testovaci_pd)

import pickle
with open("arma_exog.pk", "wb") as f:
    pickle.dump([ar_vysledek, ma_vysledek, arma_vysledek, ar_vysledek_sez,
               ma_vysledek_sez, arma_vysledek_sez], f)