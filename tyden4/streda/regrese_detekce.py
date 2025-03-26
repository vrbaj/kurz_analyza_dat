from pathlib import Path
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, LeaveOneOut, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import matplotlib.pyplot as plt

TYP_FIRMY = "mikro"
X = []
hospodarsky_vysledek = []

for soubor in Path(".", TYP_FIRMY).iterdir():
    data = pd.read_excel(soubor, sheet_name="Výkaz všech subjektů z UZ")
    print(data.shape)
    data.dropna(inplace=True, axis=1)
    print(data.shape)
    hospodarsky_vysledek.append(data["2023"].iloc[-1])
    data.drop(["Nazev Polozky", "2023"], inplace=True, axis=1)
    X.append(data.to_numpy().reshape(-1))
# print(X)
# print(hospodarsky_vysledek)
X = np.array(X)
hospodarsky_vysledek = np.array(hospodarsky_vysledek)
print(f"Velikost vstupních dat do regresního modelu {X.shape}")
print(f"Hospodářský výsledek (predikce) {hospodarsky_vysledek.shape}")
idx = np.argwhere(np.all(X[..., :] == 0, axis=0))
# print(idx)
X = np.delete(X, idx, axis=1)
print(f"Velikost X po odstranění nulových features - {X.shape}")
# mohli bysme zredukovat počet features tak, že vezmeme jenom features co
# spolu nekorelujou.. např zahodíme features co maj korelaci 0.9 až 1
# resp. -0.9 až -1
pandas_features = pd.DataFrame.from_records(X)
sns.heatmap(pandas_features.corr(), cmap="YlGnBu")
# plt.show()
# X_trenovaci, X_testovaci, y_trenovaci, y_testovaci = train_test_split(X,
#                                                                       hospodarsky_vysledek,
#                                                                       test_size = 1,
#                                                                       random_state=10)
# skalovani = StandardScaler()
# X_trenovaci = skalovani.fit_transform(X_trenovaci)
# X_testovaci = skalovani.transform(X_testovaci)
# print(np.max(X_trenovaci), np.min(X_trenovaci))
# model = Ridge(alpha=0.01)
# model.fit(X_trenovaci, y_trenovaci)
# predikce = model.predict(X_testovaci)
# print(f"Predikce {predikce}, skutečnost: {y_testovaci}")
vysledky_predikci = []
loo = LeaveOneOut()
for trenovaci_index, testovaci_index in loo.split(X):
    print(f"trenovaci_index = {trenovaci_index}")
    print(f"testovaci_index = {testovaci_index}")
