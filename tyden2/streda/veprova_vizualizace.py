import pickle
import pandas as pd
import numpy as np
import dateparser


with open("arma.pk", "rb") as f:
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
