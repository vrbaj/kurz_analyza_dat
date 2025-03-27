import numpy as np
import pandas as pd
import requests
import json
from pathlib import Path
import re
import io

from itertools import product
from tqdm import tqdm

from matplotlib import pyplot as plt
import seaborn as sns

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.varmax import VARMAX
from statsmodels.tools.sm_exceptions import EstimationWarning

from warnings import filterwarnings

# Filtrování upozornění
filterwarnings("ignore", category=EstimationWarning)

# Stažení dat o inflaci
soubor_inflace = Path("inflace_pro_mo.csv")
if not soubor_inflace.exists():
  base_url = "https://data.csu.gov.cz/api/dotaz/v1/data/vybery/"
  kod_sady = "CEN0101CT02"

  # Nacteni dat z internetu
  r = requests.get(base_url+kod_sady+"?format=JSON_STAT")

  # Zpracovani dat
  slovnik_inflace = r.json()
  nazvy_sloupcu = list(
    slovnik_inflace["dimension"]["CasM"]["category"]["index"].keys()
  )
  df_inflace = pd.DataFrame(
    np.array(slovnik_inflace["value"]).reshape(-1,len(nazvy_sloupcu)),
    columns=nazvy_sloupcu,
    index=(slovnik_inflace["dimension"]["CZCOICOP"]
                          ["category"]["label"].values())
  )

  df_inflace = df_inflace.loc[["Úhrn","Doprava"]]
  df_inflace.to_csv(soubor_inflace, index=False)
else:
  df_inflace = pd.read_csv(soubor_inflace)

# Dostanu do formatu pro spojeni
df_inflace = df_inflace.T
df_inflace.index = pd.to_datetime(df_inflace.index)
df_inflace.columns = ["Úhrn","Doprava"]
#print(df_inflace)

# Nacteni dat z xlsx souboru
soubor = Path("Dataset_MO_novy.xlsx")
tabulka = pd.ExcelFile(soubor)
print(tabulka.sheet_names)

df_spotreba = pd.read_excel(tabulka,
                            sheet_name = "Spotreba_CS_CSU_mesic",
                            index_col=0)
df_spotreba.dropna(inplace=True)
df_spotreba.columns = ["MB CS","MB CSU", "Nafta CS", "Nafta CSU"]
df_spotreba.index = pd.to_datetime(df_spotreba.index)
df_spotreba = df_spotreba.loc["2010-01-01":,:]

# df_spotreba_viz = df_spotreba.resample("YS").mean() # dalsi moznost je "MS" - na mesice a "QS" - kvartaly
# relativni = (df_spotreba_viz["MB CS"]-df_spotreba_viz["MB CSU"])/df_spotreba_viz["MB CS"]
# print(relativni)
# relativni.plot()
df_spotreba = df_spotreba[["MB CS", "Nafta CS"]]

# Nacteni dat o cene
df_ceny = pd.read_excel(tabulka,sheet_name="Ceny_MN_BA", index_col=0)
df_ceny.index = pd.to_datetime(df_ceny.index)
df_ceny = df_ceny.resample("MS").mean()
df_ceny = df_ceny.sort_index()

# nacteni dat CHMI
soubor_pocasi = Path("pocasi.csv")
if not soubor_pocasi.exists():
  url = ("https://opendata.chmi.cz" + 
        "/meteorology/climate/historical/data/monthly/")
  r = requests.get(url)
  #print(r.text)
  linky = re.findall(r'href=".*\.json"', r.text)
  linky = [link.split('"')[1] for link in linky]
  #print(linky)
  pocasi_df = pd.DataFrame()
  for link in tqdm(linky):
    r = requests.get(url+link)
    slovnik_pocasi = r.json()
    novy_radek = pd.DataFrame(
      slovnik_pocasi["data"]["data"]["values"],
      columns=slovnik_pocasi["data"]["data"]["header"].split(",")
    )
    novy_radek.drop(["FLAG_REPEAT","FLAG_INTERRUPTED"],
                    axis=1, inplace=True)
    novy_radek.dropna(inplace=True)
    novy_radek = novy_radek[novy_radek["ELEMENT"].isin(["T","SRA"])]
    pocasi_df = pd.concat([pocasi_df, novy_radek], ignore_index=True)
  pocasi_df.to_csv(soubor_pocasi,index=False)
else:
  pocasi_df = pd.read_csv(soubor_pocasi)

pocasi_df = pocasi_df[
  ((pocasi_df["ELEMENT"]=="SRA") & (pocasi_df["MDFUNCTION"]=="SUM")) |
  ((pocasi_df["ELEMENT"]=="T") & (pocasi_df["MDFUNCTION"]=="AVG") &
   (pocasi_df["TIMEFUNCTION"]=="AVG"))]
pocasi_df["datum"] = pd.to_datetime(
  pocasi_df["YEAR"].astype(str)+ "-" + 
  pocasi_df["MONTH"].astype(str) +"-01"
)
#print(pocasi_df.columns)
pocasi_df.drop(["STATION","YEAR","MONTH","MDFUNCTION","TIMEFUNCTION"],
               axis=1, inplace=True)
pocasi_df = pocasi_df.groupby(["datum","ELEMENT"]).mean().reset_index()
pocasi_df = pocasi_df.pivot(index="datum",columns="ELEMENT",
                            values="VALUE")
pocasi_df.sort_index(inplace=True)
sns.lineplot(data=pocasi_df)

# Načtení HDP
df_hdp = pd.read_csv("hdp.csv")
df_hdp = df_hdp.drop(
  ["DATAFLOW","LAST UPDATE","freq","unit",
   "s_adj","na_item","CONF_STATUS","OBS_FLAG"],
   axis=1
)
df_hdp = df_hdp.pivot(
  index="TIME_PERIOD", columns="geo", values="OBS_VALUE"
)
df_hdp.index = pd.to_datetime(df_hdp.index) + pd.DateOffset(months=2)
df_hdp.columns = ["HDP_cz", "HDP_eu"]
df_hdp.sort_index(inplace=True)


