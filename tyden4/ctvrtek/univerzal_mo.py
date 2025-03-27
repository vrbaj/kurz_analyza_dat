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
    plt.figure() # TODO secondary axis
    plt.title(f"{col} s predikovanými veličinami")
    plt.plot(spojena_data[col], label=col,
             color="yellow")
    plt.plot(spojena_data.iloc[:,0], label=spojena_data.columns[0], 
             color="green")
    plt.plot(spojena_data.iloc[:,1], label=spojena_data.columns[1], 
             color="black")
    plt.legend()

def hlavni_pipeline(endog, exog, budoucnost):
  # 1. transformovat data - "transformace_dat"
  # 2. rezdělit data na trénovací a testovací - v kódu
  # 3. hledání vhodného modelu, hledáme skrz hyperparametry 
  #       (a možná skrz modely) - TODO funkce 
  # 4. dotrénování modelu na všech datech - v kódu
  # 5. predikce budoucnosti - v kódu
  # 6. zpětná transformace dat - "zpetna_transformace_dat"
  pass

def transformace_dat(endog, exog):
  pass

def zpetna_transformace_dat(endog, exog, predikce, 
                            info_o_transformaci):
  pass

def vizualizace_predikce(predikce):
  pass

def ukladani_predikce(predikce):
  pass

###############
# Pořadí běhu příkazů
exog, endog, budoucnost = nacteni_dat()
vizualizace_dat(endog, exog)
predikce = hlavni_pipeline(endog, exog, budoucnost)
vizualizace_predikce(predikce)
ukladani_predikce(predikce)
plt.show()