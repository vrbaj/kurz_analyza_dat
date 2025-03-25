import numpy as np
import pandas as pd
import requests
import json
from pathlib import Path

from itertools import product
from tqdm import tqdm

from matplotlib import pyplot as plt
import seaborn as sns

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

