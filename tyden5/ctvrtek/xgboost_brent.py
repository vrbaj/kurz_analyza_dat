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

    # procentuální změny
    out["target_pct_change_1"] = out[target_col].shift(1).pct_change(1)
    out["target_pct_change_3"] = out[target_col].shift(1).pct_change(3)
    out["target_pct_change_12"] = out[target_col].shift(1).pct_change(12)

    return out


def add_exogenous_lag_features(df: pd.DataFrame, exog_cols: list[str]) -> pd.DataFrame:
    # externí příznaky, třeb apoměr cena ropy/index doalru
    out = df.copy()
    # cklus pro výpočet exogeních lagů
    for col in exog_cols:
        out[f"{col}_lag_1"] = out[col].shift(1)
        out[f"{col}_lag_2"] = out[col].shift(2)
        out[f"{col}_lag_3"] = out[col].shift(3)

        # klouzavý průměr
        out[f"{col}_roll_mean_3"] = out[col].shift(1).rolling(3).mean()
        # klouzavá std
        out[f"{col}_roll_std_3"] = out[col].shift(1).rolling(3).std()
        # procentuální změna
        out[f"{col}_pct_change_1"] = out[col].shift(1).pct_change(1)

    # interakční přáznaky
    # ropa/doalru
    out["brent_to_usd_ratio_lag1"] = out[TARGET_COL].shift(1) / out["usd_index"].shift(1)
    # vix/průmyslu
    out["risk_activity_mix_lag1"] = out["vix"].shift(1) / out["indpro"].shift(1)

    return out


def build_dataset() -> pd.DataFrame:
    # krok 1: stažení surových dat
    df = build_base_dataset()

    # kork 2: vypočtení kalendářních příznaků
    df = add_calendar_features(df)

    # krok 3: výpočet lagových příznaků
    df = add_target_lag_features(df, TARGET_COL)

    # krok 4: přidání exogenních příznaků
    df = add_exogenous_lag_features(df, ["usd_index", "vix", "indpro"])

    # krok 5: odstranění NaN hodnot
    df = df.dropna().copy()

    return df


# ========================================
# TRÉNOVÁNÍ A VALIDACE
# ========================================

def train_test_split_time_series(df: pd.DataFrame, test_months: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # funcke pro rozdělení data n atestovací a trénovací části
    train = df.iloc[:-test_months].copy()
    test = df.iloc[-test_months:].copy()

    return train, test

def fit_xgboost(train: pd.DataFrame, feature_cols: List[str]) -> XGBRegressor:
    # trénuje regesní model na train datech
    # rozdělit data na vstupy a výdtupy
    X_train = train[feature_cols]
    y_train = train[TARGET_COL]

    # TODO: optimalizace hyperparametrů pomocí GridSearch
    # konfogurace modelu
    model = XGBRegressor(
        # počet stromů
        n_estimators=600,
        # jak moc se nový strom učí z chyb předchozích
        learning_rate=0.05,
        # maximální hloubka stromu
        max_depth=3,
        # minimální váha vzorku vl istu
        min_child_weight=3,
        # kolik trénovacích dat každý strom vidí
        subsample=0.9,
        # strom vidí jen x % příznaků
        colsample_bytree=0.85,
        # parametry regularizace
        reg_alpha=0.0,
        reg_lambda=1.0,
        objective="reg:squarederror",
        tree_method="hist",
        random_state=RANDOM_SEED
    )

    model.fit(X_train, y_train)

    return model


def evalute_forecast(y_true: pd.Series, y_pred: pd.Series) -> None:
    # MAE
    mae = mean_absolute_error(y_true, y_pred)
    # RMSE
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    # MAPE
    mape = np.mean(np.abs((y_true, y_pred) / y_true)) * 100

    # výpis metrik
    print("Vyhodnocení")
    print(f"MAE : {mae:.3f}")
    print(f"RMSE : {rmse:.3f}")
    print(f"MAPE : {mape:.2f}%")










