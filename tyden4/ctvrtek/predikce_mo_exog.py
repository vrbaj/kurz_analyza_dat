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

# Spojení všech dat
data = pd.concat(
  [df_spotreba, df_ceny, pocasi_df, df_inflace],
  axis=1
)

for col in data.columns:
  if col in ["MB CS", "Nafta CS"]:
    resampled = data[col].resample("QS-JAN").sum()
    resampled = resampled["2010-06-01":]
    resampled.index = resampled.index + pd.DateOffset(months=2)
  elif col in ["Úhrn","Doprava"]:
    resampled = data[col].resample("QS-DEC").last()
  else:
    resampled = data[col].resample("QS-DEC").mean()
  data[col]=resampled
data = pd.concat(
  [data, df_hdp],
  axis=1
)
data = data.sort_index().dropna()
data.plot(subplots=True)
plt.figure()
sns.heatmap(data.corr(), annot=True)
data.to_excel("data_mo.xlsx")


# Transformace dat aby byla stacionární
data.columns = ['MB CS','Nafta CS','Natural 95', 'MN', 
                'SRA', 'T', 'Úhrn','Doprava', 'HDP_cz', 'HDP_eu']
exog = data[["HDP_cz"]]
endog = data[["MB CS", "Nafta CS", "Natural 95", "MN"]]

sezoni_slozky = {}
posledni_pred_diff = {}
# mezikvartální změna (jako desetinne cislo)
endog = endog.pct_change().dropna()
for col in endog.columns:
  # odstranění sezónní složky
  dekompozice = seasonal_decompose(
    endog[col], period=4, model="additive"
  )
  endog[col] = endog[col]-dekompozice.seasonal
  sezoni_slozky[col] = dekompozice.seasonal
  posledni_pred_diff[col] = endog[col].iloc[-1]
  endog[col] = endog[col].diff().dropna()

endog.dropna(inplace=True)
# spočtení testu stacionarity
for col in endog.columns:
  result = adfuller(endog[col])
  print(f"{col}: {result[1]}")

# Pro exogenní data
# mezikvartální změna (jako desetinne cislo)
exog = exog.pct_change().dropna()
for col in exog.columns:
  # odstranění sezónní složky
  dekompozice = seasonal_decompose(
    exog[col], period=4, model="additive"
  )
  exog[col] = exog[col]-dekompozice.seasonal
  if col == "HDP_cz":
    hdp_2025 = pd.DataFrame(
      [0.006, 0.006, 0.006, 0.006],
      columns=["HDP_cz"],
      index=pd.date_range("2025-01-01","2025-12-31", freq="QS-DEC")
    )
    exog = pd.concat([exog, hdp_2025])
  exog[col] = exog[col].diff().dropna()
exog.dropna(inplace=True)
# spočtení testu stacionarity
for col in exog.columns:
  result = adfuller(exog[col])
  print(f"{col}: {result[1]}")

# Příprava trénovacích dat
train = endog.loc[:"2024-01-01"]
test = endog.loc["2024-01-01":]

print(train.shape, train.index[0], train.index[-1])
print(test.shape, test.index[0], test.index[-1])
print(exog.shape, exog.index[0], exog.index[-1])

mses = []
bestmse = 1e10
for p,q,trend in tqdm(list(product(
  range(0,6), range(0,6), ["n","c","t","ct"]
  # [3], [5], ["n"]
))):
  break # pro testovani skriptu vypnuto
  try:
    model = VARMAX(train, exog=exog.loc[train.index],
                   order=(p,q), trend=trend, freq="QS-DEC")
    model_fit = model.fit(
      method="lbfgs",
      maxiter=100
    )
    mse = model_fit.predict(
      start=test.index[0], end=test.index[-1],
      exog=exog.loc[test.index]
    ).sub(test).pow(2).mean().mean()
    mses.append(mse)
    if mse < bestmse:
      bestmse = mse
      bestmodel = model_fit
      bestorder = (p,q)
      besttrend = trend
  except Exception as e:
    print(e)
    mses.append(np.nan)

# pro usporu rychlosti
bestmse = 0.028
bestorder = (3,5)
besttrend = "n"

print(f"Nejlepší mse: {bestmse:.5f}")
print(f"Nejlepší parametry: {bestorder}, {besttrend}")
print(mses)

# Natrénování modelu po identifikaci optimálních parametrů
model = VARMAX(
  endog,
  exog = exog.loc[endog.index],
  order = bestorder,
  trend = besttrend,
  freq="QS-DEC"
)
model_fit = model.fit(
  method="nm",
  maxiter=100,
)
predpoved = model_fit.get_forecast(
  steps = 4,
  exog = exog.iloc[-4:,:]
)
#print(predpoved.predicted_mean)
pred = predpoved.predicted_mean

for col in pred.columns:
  pred[col].iloc[0] += posledni_pred_diff[col]
  pred[col] = pred[col].cumsum()
  pred[col] = pred[col] + sezoni_slozky[col][-4:].values + 1

pred.iloc[0,:] = pred.iloc[0,:]*data.iloc[-1,data.columns.get_indexer(
  pred.columns
)]
pred = pred.cumprod()
print(pred)
print(pred.sum())
