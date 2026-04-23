# definovanání použitých knihoven/modulů

import warnings
from dataclasses import dataclass
from typing import Tuple, List, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

# potlačení varování pomocí knihovny warnings
warnings.filterwarnings("ignore")

# nahrání dat z webu
SERIES_URLS: Dict[str,str] = {
    # denní cena ropy brent
    "brent": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU",
    # index dolaru
    "usd_index": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS",
    # index volatility
    "vix": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS",
    # index průmyslové produkce USA
    "indpro": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO",
}

# definice cílového sloupce
TARGET_COL = "brent_monthly_avg"
# počet testovácích měsíců
TEST_MONTHS = 24
# fixní seed pro reprodukovatelnost
RANDOM_SEED = 42


# definice dekorátoru
@dataclass
class ForecastResult:
    model:XGBRegressor
    data: pd.DataFrame
    train: pd.DataFrame
    test: pd.DataFrame
    feature_cols: List[str]
    predictions: pd.Series

# =================================================
# FUNKCE PRO STAHOVÁNÍ DAT
# =================================================

def load_fred_series(series_id: str, value_name: str) -> pd.DataFrame:
    # funkce pro stahování dadt ze stránky fred
    # získání url adresy ze slovníku
    url = SERIES_URLS[series_id]
    # stažení do csv (umí z url adresi nativně)
    df = pd.read_csv(url)
    # přejmenování datumu a převod na datumový formát
    df["DATE"] = pd.to_datetime(df["observation_date"])
    # odstranění starého textového datumu
    df.drop(["observation_date"], axis=1, inplace=True)
    # nalezení hodnotového lsoupce
    original_value_col = [c for c in df.columns if c != "DATE"][0]
    # převod na čísla (fred nahrazuje chybející hodnoty .
    df[original_value_col] = pd.to_numeric(df[original_value_col], errors="coerce")
    # přejmenování sloupce s ropou
    df = df.rename(columns={original_value_col: value_name})
    # odstranění řádků s NaN
    df = df.dropna(subset=[value_name]).copy()
    # nastavení datumového sloupce jako index
    df = df.set_index("DATE").sort_index()

    return df




df = load_fred_series("brent","nic")
print(df.head())




