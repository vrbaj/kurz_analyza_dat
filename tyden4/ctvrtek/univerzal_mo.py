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

def nacteni_dat(nazev_souboru="data_mo.xlsx"):
  # nactu soubor
  soubor = pd.ExcelFile(nazev_souboru)
  # overeni souboru
  print(soubor.sheet_names)
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

nacteni_dat()