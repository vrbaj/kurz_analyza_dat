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
plt.show()