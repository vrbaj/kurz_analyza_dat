from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

TYP_FIRMY = "mikro"
X = []
hospodarsky_vysledek = []

for soubor in Path(".", TYP_FIRMY).iterdir():
    data = pd.read_excel(soubor, sheet_name="Výkaz všech subjektů z UZ")
    print(data.shape)
    data.dropna(inplace=True, axis=1)
    print(data.shape)
    data.drop(["Nazev Polozky"], inplace=True, axis=1)
    X.append(data.to_numpy().reshape(-1))
# print(X)
# print(hospodarsky_vysledek)
X = np.array(X)

print(f"Velikost vstupních dat do regresního modelu {X.shape}")

idx = np.argwhere(np.all(X[..., :] == 0, axis=0))
# print(idx)
X = np.delete(X, idx, axis=1)
print(f"Velikost X po odstranění nulových features - {X.shape}")
# mohli bysme zredukovat počet features tak, že vezmeme jenom features co
# spolu nekorelujou.. např zahodíme features co maj korelaci 0.9 až 1
# resp. -0.9 až -1
pandas_features = pd.DataFrame.from_records(X)
iso_forest = IsolationForest(contamination=0.05, random_state=10)
anomalie = iso_forest.fit_predict(pandas_features)
print(anomalie)

data_z_arx = pd.read_csv("mikro_arx_predikce.csv")
print(data_z_arx.columns)
data_z_arx.drop(["Unnamed: 0", "soubor", "predikovana_hodnota", "chyba_predikce"],
                inplace=True, axis=1)
print(data_z_arx.columns)
iso_forest_arx = IsolationForest(contamination=0.05, random_state=42)
print(iso_forest_arx.fit_predict(data_z_arx))