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


def to_monthly_mean(df: pd.DataFrame, col: str) -> pd.DataFrame:
    # funkce na převod denních dat na měsíční průměry
    return df[[col]].resample("MS").mean()

def to_monthly_last(df:pd.DataFrame, col: str) -> pd.DataFrame:
    # vrací poslední hodntou v měsíci
    return df[[col]].resample("MS").last()

# =======================================
# SESTAVENÍ DATASETU
# ======================================

def build_base_dataset() -> pd.DataFrame:
    # funkce pro sestavení datasetu ze všech odkazů
    # stažení surových dat
    brent_daily = load_fred_series("brent", "brent")
    usd_daily = load_fred_series("usd_index", "usd_index")
    vix_daily = load_fred_series("vix", "vix")
    indpro_monthly = load_fred_series("indpro", "indpro")

    # převod ropy na měsíční prměr
    brent_m = to_monthly_mean(brent_daily, "brent").rename(columns={"brent": TARGET_COL})
    # měsíční průměr síly dolaru
    usd_m = to_monthly_mean(usd_daily, "usd_index")
    # měsíční průměr vix indexu
    vix_m = to_monthly_mean(vix_daily, "vix")
    # resample jen pro unifikaci indexu
    indpro_m = indpro_monthly[["indpro"]].resample("MS").last()

    # spojení datových řad do jednoho dataframu
    df = brent_m.join([usd_m, vix_m, indpro_m], how="inner")

    return df

# =========================================
# FEATER ENGINEERING
# =========================================

def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    # přidáme kalendářní příznaky do dataframu
    # uděláme si kopii dataframu ať nemodifikujem původní
    out = df.copy()
    # číslo měsíce z indexu
    out["month"] = out.index.month
    # extrakce kvartálu z datumu
    out["quarter"] = out.index.quarter
    # sinosová složka měsíce
    out["month_sin"] = np.sin(2 * np.pi * out["month"] / 12)
    # kosinová složka měsíce
    out["month_cos"] = np.cos(2 * np.pi * out["month"] / 12)

    return out


def add_target_lag_features(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    # funkcepro výpočet lagovýych příznaků
    out = df.copy()

    # lagové příznaky
    for lag in [1, 2, 3, 6, 12]:
        # tvorba lagových sloupců
        out[f"target_lag_{lag}"] = out[target_col].shift(lag)

    # klouzávé průměry
    out["target_roll_mean_3"] = out[target_col].shift(1).rolling(3).mean()
    out["target_roll_mean_6"] = out[target_col].shift(1).rolling(6).mean()
    out["target_roll_mean_12"] = out[target_col].shift(1).rolling(12).mean()

    # klouzavá volatilita
    out["target_roll_std_3"] = out[target_col].shift(1).rolling(3).std()
    out["target_roll_std_6"] = out[target_col].shift(1).rolling(6).std()
    out["target_roll_std_12"] = out[target_col].shift(1).rolling(12).std()

    # momentum
    out["target_mom_1"] = out[target_col].shift(1) - out[target_col].shift(2)
    out["target_mom_3"] = out[target_col].shift(1) - out[target_col].shift(4)

    #



df = build_base_dataset()
out = add_calendar_features(df)
print(out.head())
