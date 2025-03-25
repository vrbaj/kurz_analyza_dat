import numpy as np
import pandas as pd
import requests
import json
from pathlib import Path

from itertools import product
from tqdm import tqdm

from matplotlib import pyplot as plt
import seaborn as sns

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.vector_ar.vecm import VECM
from statsmodels.tsa.statespace.varmax import VARMAX

# Stažení dat z ČSÚ o inflaci
if not Path("inflace.csv").exists():
  base_url = "https://data.csu.gov.cz/api/dotaz/v1/data/vybery/"
  kod_sady = "CEN0101CT02"
  r = requests.get(base_url+kod_sady+"?format=JSON_STAT")

  slovnik_inflace = r.json()
  nazvy_sloupcu = list(slovnik_inflace["dimension"]["CasM"]
                                    ["category"]["index"].keys())

  df_inflace = pd.DataFrame(np.array(slovnik_inflace["value"]).reshape(-1,len(nazvy_sloupcu)),
                          columns=nazvy_sloupcu, 
                          index = (slovnik_inflace["dimension"]["CZCOICOP"]
                                                  ["category"]["label"].values())
                          )

  df_inflace = df_inflace.loc[["Úhrn"]]
  df_inflace = df_inflace.iloc[:,2::3]
  print(df_inflace)
  df_inflace.to_csv("inflace.csv")
else:
  df_inflace = pd.read_csv("inflace.csv")

# CZ and EU HDP (Eurostat) - https://ec.europa.eu/eurostat/databrowser/bookmark/f7d74afe-7ade-46c4-a17b-9a92abee7693?lang=en
df_hdp = pd.read_csv("hdp.csv")
df_hdp = df_hdp.drop(["DATAFLOW","LAST UPDATE","freq","unit",
                      "s_adj","na_item","CONF_STATUS","OBS_FLAG"],axis=1)
df_hdp = df_hdp.pivot(index="geo", columns="TIME_PERIOD", values="OBS_VALUE")
#print(df_hdp)

# Poptávka na trhu práce (eurostat) - https://ec.europa.eu/eurostat/databrowser/bookmark/6a758b9d-2ca4-4993-8b83-d21fdab92b4e?lang=en
df_prace = pd.read_csv("labor_demand.csv")
df_prace = df_prace.pivot(index="geo", columns="TIME_PERIOD", values="OBS_VALUE")
#print(df_prace)

# Data pro reposazbu
df_sazba = pd.read_csv("reposazba.csv",delimiter=";",decimal=",")
df_sazba.index = pd.to_datetime(df_sazba["Období"])
df_sazba = df_sazba.resample("QS-DEC").first()
df_sazba = df_sazba.drop(["Období","Unnamed: 2"] ,axis=1)
df_sazba.columns = ["sazba"]
#print(df_sazba)

# Pro sloučení dat na stejný časový index
def kvartal_na_datum(q: str):
  rok, cislo = q.split("-Q")
  mesic = int(cislo)*3
  return pd.to_datetime(f"{rok}-{mesic:02d}-01")

# priprava hdp pro slouceni
df_hdp.columns = [kvartal_na_datum(q) for q in df_hdp.columns]
df_hdp.index = ["HDP_cz","HDP_eu"]
df_hdp = df_hdp.T
#print(df_hdp)

# priprava prace pro slouceni
df_prace.columns = [kvartal_na_datum(q) for q in df_prace.columns]
df_prace.index = ["trh_prace_cz"]
df_prace = df_prace.T
#print(df_prace)

# priprava inflace pro slouceni
df_inflace = df_inflace.set_index(df_inflace.columns[0])
df_inflace = df_inflace.T
df_inflace.index = pd.to_datetime(df_inflace.index)
df_inflace.columns = ["Inflace"]
#print(df_inflace)

# priprava sazby pro slouceni
df_sazba = df_sazba/100
#print(df_sazba)

# sloučení dat
data = pd.concat([df_hdp,df_prace,df_inflace,df_sazba],axis=1)
data = data.dropna(axis=0)
data.plot(subplots=True)

# Odstranění sezónní složky
plt.figure()
for idx, col in enumerate(["HDP_cz","HDP_eu","Inflace"]):
  sezonni_slozka = seasonal_decompose(data[col],
                                      model="multiplicative",
                                      period=4).seasonal
  data[col] = data[col]/sezonni_slozka
  plt.subplot(3,2,2*idx+1)
  plt.plot(sezonni_slozka)
  plt.title("Sezónní složka: "+col)
  plt.xticks(rotation=45)
  plt.subplot(3,2,2*idx+2)
  plt.plot(data[col])
  plt.title(col)
  plt.xticks(rotation=45)
plt.tight_layout()

#### Vytovoření stacionárních dat
delta_data = data.copy(deep=True)

# přepočítám na meziroční změny (v %) pro slopce kde to má smysl
cols = ["HDP_cz","HDP_eu","Inflace","trh_prace_cz"]
delta_data[cols] = delta_data[cols].pct_change(periods=4, freq="QS-DEC")
delta_data = delta_data.dropna()
delta_data.plot(subplots=True)

# uložím první řádek pro pozdější rekonstrukci
data_pro_rek = delta_data.iloc[0]
print(data_pro_rek)

# udělám diferenci
delta_data = delta_data.diff(axis=0).dropna()
delta_data.plot(subplots=True)

# uložim si data pro ukázku výpočtu predikce
hdp_q4_2024 = data["HDP_cz"].loc["2024-12-01"]
hdp_q4_2023 = data["HDP_cz"].loc["2023-12-01"]

# Ukázka že jsem schopen rekonstruovat původní data z diferencí
hdp_rec = delta_data["HDP_cz"]
hdp_rec[hdp_rec.index[0]-pd.tseries.offsets.QuarterBegin(1)] = \
  data_pro_rek["HDP_cz"]
hdp_rec = hdp_rec.sort_index()
hdp_rec = hdp_rec.cumsum()
print(hdp_q4_2024)
print(hdp_q4_2023*(1+hdp_rec.loc["2024-12-01"]))

# Test na stacionaritu
for col in delta_data.columns:
  series = delta_data[col]
  test = adfuller(series)
  print(f"{col+':':{' '}<16}pval: {test[1]:.4f}")


# Rozdělení dat train-val-test
train = delta_data.loc[:"2022-12-01"] # pro trénování modelu
val = delta_data.loc["2023-03-01":"2023-12-01"] # pro výběr řádu
test = delta_data.loc["2024-03-01":"2024-12-01"] # pro predikci
print(train.shape,val.shape,test.shape)

############ VAR model
print("#"*50)
print("VAR")
model = VAR(train, freq="QS-DEC")
# výběr řádu modelu
best_mse = 1e10

# vybíráme z maximálních řádů 1-7 a z trendů "n","c","ct"
for order, trend in tqdm(list(
                         product(range(1,8),
                                 ["n","c","ct"]))):
  # fit modelu
  model_results = model.fit(order, trend=trend, ic="fpe")
  # predikce 4 následujících hodnot
  predikce = model_results.forecast(y=train.to_numpy(), steps=4)
  # spočtení chyby predikce
  mse = np.mean((val.to_numpy()-predikce)**2)
  # nejlepší model uložíme
  if mse < best_mse:
    best_mse = mse
    best_order = order
    best_trend = trend
    best_results = model_results
    best_predikce = predikce

# vypíšeme model
print(f"Nejlepší model: {best_order} {best_trend}")
print(f"MSE: {best_mse:.4f}")
#print(best_results.summary())

# Vypočtení predikce
train_val = pd.concat([train,val])
model = VAR(train_val, freq="QS-DEC")
model_results = model.fit(best_order, trend=best_trend, ic="fpe")
predikce = model_results.forecast(y=train_val.to_numpy(), steps=4)
predikce = pd.DataFrame(predikce, columns=test.columns, index=test.index)
predikce_val = pd.DataFrame(best_predikce, columns=val.columns,
                            index=val.index)

# Definice funkce pro zobrazení predikce
def zobrazeni_predikce_2024(predikce, val, test, train, predikce_val):
  col = "HDP_cz"
  train_val = pd.concat([train,val])

  plt.figure()
  sns.lineplot(data=train_val, x=train_val.index, y=col, label="HDP")
  sns.lineplot(data=test, x=test.index, y=col, label="HDP 2024")
  sns.lineplot(data=predikce, x=predikce.index, y=col, label="predikce")
  sns.lineplot(data=predikce_val, x=predikce_val.index, y=col,
               label="predikce val")

  vysledny_df = pd.concat([train_val,predikce])
  vysledny_df.loc[vysledny_df.index[0]-pd.tseries.offsets.QuarterBegin(1),
                  :] = data_pro_rek
  vysledny_df = vysledny_df.sort_index()
  vysledny_df = vysledny_df.cumsum()
  predikce_yy = vysledny_df[col].loc["2024-12-01"]
  predikce_q4_2024 = hdp_q4_2023*(1+predikce_yy)

  print("-"*50)
  print(f"Predikce pro Q4 2024")
  print("Má vyjít:", hdp_q4_2024)
  print("Predikce:", predikce_q4_2024)
  print(f"Meziroční změna: {predikce_yy:.2%}")

zobrazeni_predikce_2024(predikce, val, test, train, predikce_val)

# VECM - vsechny jako interni
print("#"*50)
print("VECM - pouze interni promenne")

best_mse=1e10
for order in tqdm(range(1,10)):
  # definujeme model
  model = VECM(train, freq="QS-DEC",
               deterministic="ci",
               k_ar_diff=order,
               seasons=4)
  # trénujeme
  results = model.fit()
  # predikujeme
  predikce = results.predict(steps=4)
  # spočteme průměrnou kvadratickou odchylku
  mse = np.mean((predikce - val.to_numpy())**2)
  if best_mse>mse:
    best_mse = mse
    best_order = order
    best_results = results
    best_predikce = predikce

print("Nejlepší model:", best_order)
print(f"MSE: {best_mse:.4f}")

# Vypočtení predikce
model = VECM(train_val, freq="QS-DEC",
             deterministic="ci",
             k_ar_diff=best_order,
             seasons=4)
results = model.fit()
predikce = results.predict(steps=4)
predikce = pd.DataFrame(predikce, columns=test.columns,
                        index=test.index)
predikce_val = pd.DataFrame(best_predikce, columns=val.columns,
                            index = val.index)
# Zobrazení VECM predikce
zobrazeni_predikce_2024(predikce, val, test, train,predikce_val)

# VAR s externim
print("#"*50)
print("VAR - s externimi promennymi")

# pripravim data
train_int = train[["HDP_cz","HDP_eu","Inflace","trh_prace_cz"]]
val_int = val[["HDP_cz","HDP_eu","Inflace","trh_prace_cz"]]
ext_data = data[["sazba"]]

# hledam nejlepsi model
model = VAR(train_int, exog=ext_data.loc[train.index], freq="QS-DEC")
best_mse = 1e10
for order, trend in tqdm(list(product(range(1,8),["n","c","ct"]))):
  results = model.fit(order, trend=trend)
  predikce = results.forecast(y=train_int.to_numpy(),
                              steps=4,
                              exog_future=ext_data.loc[val.index])
  mse = np.mean((val_int.to_numpy() - predikce)**2)
  if mse < best_mse:
    best_mse = mse
    best_order = order
    best_trend = trend
    best_results = results
    best_predikce = predikce

print(f"Nejlepší model: {best_order} {best_trend}")
print(f"MSE: {best_mse:.4f}")

# Vypočtení predikce
train_val_int = pd.concat([train_int,val_int])
model = VAR(train_val_int,
            exog=ext_data.loc[train_val_int.index],
            freq = "QS-DEC")
model_results = model.fit(best_order, trend=best_trend)
predikce = model_results.forecast(y=train_val_int.to_numpy(),
                                  steps=4,
                                  exog_future=ext_data.loc[test.index])
predikce = pd.DataFrame(predikce, columns=train_int.columns,
                        index=test.index)
predikce_val = pd.DataFrame(best_predikce, columns = val_int.columns,
                            index=val_int.index)
zobrazeni_predikce_2024(predikce, val, test, train, predikce_val)



plt.show()