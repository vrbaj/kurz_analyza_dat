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

from sklearn.linear_model import Ridge

from warnings import filterwarnings

# Filtrování upozornění
filterwarnings("ignore", category=EstimationWarning)

###############
# Definice funkcí

def dopredikuj(endog):
  # dopredikujeme jednotlivé sloupce 
  # až do maximálního indexu
  # např. SARIMA
  return endog

def nacteni_dat(nazev_souboru="data_mo.xlsx"):
  # nactu soubor
  soubor = pd.ExcelFile(nazev_souboru)
  # overeni souboru
  listy_ok = all([nazev_list in ["exog","endog"] for nazev_list
                  in soubor.sheet_names])
  assert listy_ok, "Špatný formát souboru"
  # nacteni dat
  endog = pd.read_excel(soubor, sheet_name="endog", index_col=0)
  exog = pd.read_excel(soubor, sheet_name="exog", index_col=0)
  endog.index = pd.to_datetime(endog.index)
  exog.index = pd.to_datetime(exog.index)

  # overim zda se indexy prekryvaji
  spolecne_indexy = endog.index.intersection(exog.index)
  assert len(spolecne_indexy) > 0, "Data se nepřekrývají"

  # co chci predikovat 
  budoucnost = exog.index.difference(endog.index)
  budoucnost = budoucnost[budoucnost>endog.index[-1]]
  assert len(budoucnost) > 0, "Není definované období pro predikci"

  # overim ze data nejsou prazdna
  assert exog.shape[0] > 0 and exog.shape[1] > 0, "Exogenní data jsou špatně"
  assert endog.shape[0] > 0 and endog.shape[1] > 0, "Endogenní data jsou špatně"

  # Do budoucnosti co by mohlo být implementováno
  endog = dopredikuj(endog)

  return exog, endog, budoucnost

def vizualizace_dat(endog, exog):
  # zobrazení všech dat v závislosti na čase
  endog.plot(subplots=True)
  plt.suptitle("Endogenní data")
  plt.tight_layout()
  plt.savefig("endogenni_data.png")
  exog.plot(subplots=True)
  plt.suptitle("Exogenní data")
  plt.tight_layout()
  plt.savefig("exogenni_data.png")

  # zobrazení korelační matice
  spojena_data = pd.concat([endog,exog], axis=1).dropna()
  plt.figure()
  sns.heatmap(
    spojena_data.corr(),
    annot=True,
  )
  plt.title("Korelační matice pro všechna data")
  plt.savefig("korelacni_matice.png")

  for col in spojena_data.columns[2:]:
    plt.figure()
    spojena_data[col].plot(label=col, color="yellow", legend=True)
    spojena_data.iloc[:,0].plot(label=spojena_data.columns[0],
                                color="green", secondary_y=True, legend=True)
    spojena_data.iloc[:,1].plot(label=spojena_data.columns[1],
                                color="black", secondary_y=True, legend=True)
    plt.title(f"Graf pro {col} a predikované sloupce")
    plt.tight_layout()
    plt.savefig(f"graf_{col}.png")


def hlavni_pipeline(endog, exog, budoucnost):
  # covidova data filtrace
  covid_index = endog.index
  covid_index = covid_index[(
    (covid_index >= "2020-01-01") &
    (covid_index <= "2021-12-31")
  )]

  # 1. transformovat data
  trenovaci_data = pd.concat(
    [exog, endog.iloc[:, 2:]],
    axis=1
  )
  for col in endog.columns[:2]:
    for i in range(1,5):
      trenovaci_data[f"{col}_{i}"]= endog[col].shift(i)
  trenovaci_data = trenovaci_data.dropna()

  # 2. rezdělit data na trénovací a testovací
  train_index = trenovaci_data.index[:-len(budoucnost)]
  test_index = trenovaci_data.index[-len(budoucnost):]
  train_index = train_index[~train_index.isin(covid_index)]
  test_index = test_index[~test_index.isin(covid_index)]

  # 3. hledání vhodného modelu, hledáme skrz hyperparametry 
  best_mse = np.inf
  for alpha in [0, 1e-2, 1e-1, 1, 1e1, 1e2]:
    model = Ridge(alpha=alpha)
    model.fit(
      trenovaci_data.loc[train_index[1:] - pd.DateOffset(months=3)],
      endog.loc[train_index[1:]]
    )

    predikce_df = pd.DataFrame(index=test_index, columns=endog.columns)
    predikcni_data = trenovaci_data.loc[train_index]

    for timestep in test_index:
      # predikce pro každý timestep
      #print(predikcni_data.loc[[timestep-pd.DateOffset(months=3)]])
      predikce = model.predict(predikcni_data.loc[[timestep-pd.DateOffset(months=3)]])
      predikce_df.loc[timestep] = predikce

      # doplnim si data pro další predikci
      predikcni_data.loc[timestep] = predikce_df.loc[timestep,:]
      predikcni_data.loc[timestep] = exog.loc[timestep]
      if len(endog.columns) > 2:
        predikcni_data.loc[timestep, endog.columns[2:]] = endog.loc[timestep, endog.columns[2:]]
      for col in endog.columns[:2]:
        for i in range(1,5):
          if i == 1:
            predikcni_data.loc[timestep, f"{col}_{i}"] = predikce_df.loc[timestep, col]
          else:
            predikcni_data.loc[timestep, f"{col}_{i}"] = \
              predikcni_data.loc[timestep-pd.DateOffset(months=3), f"{col}_{i-1}"]
    # vyhodnoceni predikce
    mse = np.mean(
      ((predikce_df.loc[test_index, endog.columns[:2]]) - \
      (endog.loc[test_index, endog.columns[:2]]))**2
    )
    if mse < best_mse:
      best_mse = mse
      best_model = model
      predikce_val = predikce_df
  print(f"Nejlepší model s MSE: {best_mse}")
  print(best_model)

  # 4. dotrénování modelu na všech datech - v kódu
  indexy = trenovaci_data.index
  indexy = indexy[~indexy.isin(covid_index)]

  best_model.fit(
    trenovaci_data.loc[indexy[1:] - pd.DateOffset(months=3)],
    endog.loc[indexy[1:]]
  )


  # 5. predikce budoucnosti - v kódu
  predikce_df = pd.DataFrame(index=budoucnost, columns=endog.columns)
  predikcni_data = trenovaci_data
  for timestep in budoucnost:
    predikce = best_model.predict(
      predikcni_data.loc[[timestep-pd.DateOffset(months=3)]]
    )
    predikce_df.loc[timestep] = predikce
    # doplnim si data pro dalsi predikci
    predikcni_data.loc[timestep] = exog.loc[timestep]
    if len(endog.columns) > 2:
      predikcni_data.loc[timestep, endog.columns[2:]] = predikce_df.loc[timestep, endog.columns[2:]] 
    for col in endog.columns[:2]:
      for i in range(1,5):
        if i == 1:
          predikcni_data.loc[timestep, f"{col}_{i}"] = predikce_df.loc[timestep, col]
        else:
          predikcni_data.loc[timestep, f"{col}_{i}"] = \
            predikcni_data.loc[timestep-pd.DateOffset(months=3), f"{col}_{i-1}"]
    
  # 6. zpětná transformace dat
  # -> není potřeba, protože se transformace dat neprovádí
  return predikce_df, predikce_val

def vizualizace_predikce(predikce, predikce_val, endog, exog):
  for col in endog.columns[:2]:
    plt.figure()
    # vizualizace predikce_val
    predikce_val[col].plot(label="predikce", color="black", legend=True, linestyle="--")
    # skutecnost
    endog[col].plot(label="Realna data", color="blue", legend=True)
    # vizualizace budoucnosti (oos predikce)
    predikce[col].plot(label="Predikce do budoucnosti", color="red", legend=True,
                       linestyle="--", marker="x")
    # zbytek
    plt.suptitle(f"Predikce pro {col}")
    plt.tight_layout()
    plt.savefig(f"predikce_{col}.png")

def ukladani_predikce(predikce, endog, exog):
  # ulozeni dat
  with pd.ExcelWriter("predikce.xlsx") as soubor:
    exog.to_excel(soubor, sheet_name="exog")
    endog.to_excel(soubor, sheet_name="endog")
    predikce.to_excel(soubor, sheet_name="predikce")

###############
# Pořadí běhu příkazů
exog, endog, budoucnost = nacteni_dat()
vizualizace_dat(endog, exog)
predikce, predikce_val = hlavni_pipeline(endog, exog, budoucnost)
vizualizace_predikce(predikce, predikce_val, endog, exog)
ukladani_predikce(predikce, endog, exog)
plt.show()