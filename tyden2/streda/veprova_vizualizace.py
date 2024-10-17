import pickle
import pandas as pd
import numpy as np
import dateparser
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

with open("arma_exog.pk", "rb") as f:
    vysledek = pickle.load(f)
(ar_vysledek, ma_vysledek, arma_vysledek,
 ar_vysledek_s, ma_vysledek_s, arma_vysledek_s) = vysledek
print(f'AR - {ar_vysledek["model"]} - RMSE: {ar_vysledek["rmse"]}')
print(f'MA - {ma_vysledek["model"]} - RMSE: {ma_vysledek["rmse"]}')
print(f'ARMA - {arma_vysledek["model"]} - RMSE: {arma_vysledek["rmse"]}')
print(f'ARs - {ar_vysledek_s["model"]} - RMSE: {ar_vysledek_s["rmse"]}')
print(f'MAs - {ma_vysledek_s["model"]} - RMSE: {ma_vysledek_s["rmse"]}')
print(f'ARMAs - {arma_vysledek_s["model"]} - RMSE: {arma_vysledek_s["rmse"]}')

# reprodukovatelnost
np.random.seed(42)
# načteme tabulku dat
data = pd.read_excel("vyvoj_cen_jidlo_upraveno.xlsx")
data["datum"] = data["datum"].apply(lambda x: dateparser.parse(x))
# převedení na datetime
data["datum"] = pd.to_datetime(data["datum"])
# setřídění dat od nejstarších po nejnovější
data.sort_values(by="datum", inplace=True)
data.set_index("datum", inplace=True)
data.index = pd.DatetimeIndex(data.index).to_period("M")
# připrava dat na trénvací a testovací
trenovaci_velikost = int(len(data["Vepřová pečeně [1 kg]"]) * 0.9)
testovaci_data = data["Vepřová pečeně [1 kg]"][trenovaci_velikost:]
# příprava osy x
x = range(0, len(testovaci_data), 1)
popisky = [str(popisek) for popisek in testovaci_data.index]
for vys in vysledek:
    fig, ax = plt.subplots(1, 1)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.plot(x, testovaci_data, label="Testovaci data")
    ax.plot(x, vys["predikce"], label="Predikce")
    fig.legend()
    plt.title(vys["model"])
    plt.xticks(ticks=x, labels=popisky)
plt.show()