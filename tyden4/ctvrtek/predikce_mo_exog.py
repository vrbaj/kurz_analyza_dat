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

  r = requests.get(base_url+kod_sady+"?format=JSON_STAT")

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