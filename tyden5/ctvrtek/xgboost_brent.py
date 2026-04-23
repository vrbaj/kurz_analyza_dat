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
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    # výpis metrik
    print("Vyhodnocení")
    print(f"MAE : {mae:.3f}")
    print(f"RMSE : {rmse:.3f}")
    print(f"MAPE : {mape:.2f}%")


def walk_forward_one_step(df: pd.DataFrame, feature_cols: List[str], test_months: int) -> pd.Series:
    # založení seznamů
    preds = []
    pred_index = []

    # nastavení prvního indexu
    start_idx = len(df) - test_months

    # cyklus iterující přes každý měsíc v testu
    for i in range(start_idx, len(df)):
        # trénovací data, před aktuálním testovacím bodem
        train_slice = df.iloc[:i].copy()
        # to samé pro testovací
        test_row = df.iloc[[i]].copy()
        # natrénování modelu
        model = fit_xgboost(train_slice, feature_cols)
        # predicke pro aktuální měsíc
        pred = model.predict(test_row[feature_cols])[0]
        # uložení predikcí do listu
        preds.append(pred)
        pred_index.append(test_row.index[0])

    return pd.Series(preds, index=pred_index, name="prediction")


def feature_importance_table(model: XGBRegressor, feature_cols: List[str]) -> pd.DataFrame:
    # vrací nám tabulku s feature importance
    imp = pd.DataFrame(
        {"feature": feature_cols, "importance": model.feature_importances_}
    )

    # seřazení příznáků
    imp = imp.sort_values("importance", ascending=False)

    return imp

# ============================================
# Predicke
# =============================================

def fit_and_predict() -> ForecastResult:
    # hlavní pipelina, seskipení všech ostatních funkcí a spuštění tréningu

    # postavení datasetu z příznaků
    df = build_dataset()

    # časový split dat
    train, test = train_test_split_time_series(df, TEST_MONTHS)

    # vyhození některých exogeních sloupců (ať model nepužívá to co nemá v reálném čase)
    raw_exog_cols = ["usd_index", "vix", "indpro"]
    feature_cols = [c for c in df.columns if c != TARGET_COL and c not in raw_exog_cols]

    model = fit_xgboost(train, feature_cols)

    # predikci na testovacích datech
    predictions = pd.Series(
        model.predict(test[feature_cols]),
        index=test.index,
        name="prediction",
    )

    return ForecastResult(
        model=model,
        data=df,
        train=train,
        test=test,
        feature_cols=feature_cols,
        predictions=predictions
    )


def make_next_month_feature_row(df:pd.DataFrame) -> pd.DataFrame:
    # lagové příznaky pro predicke
    # index posledního měsíce
    last_idx = df.index[-1]
    # nastavení datumu příštího měsíce
    next_idx = last_idx + pd.offsets.MonthBegin(1)

    # kopie dataframu
    s = df[TARGET_COL].copy()
    usd = df["usd_index"].copy()
    vix = df["vix"].copy()
    indpro = df["indpro"].copy()

    row = {
        # kalendářní přznaky
        "month": next_idx.month,
        "quarter": next_idx.quarter,
        "month_sin": np.sin(2 * np.pi * next_idx.month / 12),
        "month_cos": np.cos(2 * np.pi * next_idx.month / 12),

        # lagy
        "target_lag_1": s.iloc[-1],
        "target_lag_2": s.iloc[-2],
        "target_lag_3": s.iloc[-3],
        "target_lag_6": s.iloc[-6],
        "target_lag_12": s.iloc[-12],

        # klouzavé průměry
        "target_roll_mean_3": s.iloc[-3].mean(),
        "target_roll_mean_6": s.iloc[-6].mean(),
        "target_roll_mean_12": s.iloc[-12].mean(),

        # volatilita
        "target_roll_std_3": s.iloc[-3].std(),
        "target_roll_std_6": s.iloc[-6].std(),
        "target_roll_std_12": s.iloc[-12].std(),

        # momentum
        "target_mom_1": s.iloc[-1] - s.iloc[-2],
        "target_mom_3": s.iloc[-1] - s.iloc[-4],

        # target procentuální změny
        "target_pct_change_1": (s.iloc[-1] - s.iloc[-2]) / s.iloc[-2],
        "target_pct_change_3": (s.iloc[-1] - s.iloc[-4]) / s.iloc[-4],
        "target_pct_change_12": (s.iloc[-1] - s.iloc[-13]) / s.iloc[-13],

        # usd index feature
        "usd_index_lag_1": usd.iloc[-1],
        "usd_index_lag_2": usd.iloc[-2],
        "usd_index_lag_3": usd.iloc[-3],
        "usd_index_roll_mean_3": usd.iloc[-3:].mean(),
        "usd_index_roll_std_3": usd.iloc[-3:].std(),
        "usd_index_pct_change_1": (usd.iloc[-1] - usd.iloc[-2]) / usd.iloc[-2],

        # vix index features
        "vix_lag_1": vix.iloc[-1],
        "vix_lag_2": vix.iloc[-2],
        "vix_lag_3": vix.iloc[-3],
        "vix_roll_mean_3": vix.iloc[-3:].mean(),
        "vix_roll_std_3": vix.iloc[-3:].std(),
        "vix_pct_change_1": (vix.iloc[-1] - vix.iloc[-2]) / vix.iloc[-2],

        # indpro index
        "indpro_lag_1": indpro.iloc[-1],
        "indpro_lag_2": indpro.iloc[-2],
        "indpro_lag_3": indpro.iloc[-3],
        "indpro_roll_mean_3": indpro.iloc[-3:].mean(),
        "indpro_roll_std_3": indpro.iloc[-3:].std(),
        "indpro_pct_change_1": (indpro.iloc[-1] - indpro.iloc[-2]) / indpro.iloc[-2],

        # interakční features
        "brent_to_usd_ratio_lag1": s.iloc[-1] / usd.iloc[-1],
        "risk_activity_mix_lag1": vix.iloc[-1] / indpro.iloc[-1],
    }

    return pd.DataFrame([row], index=[next_idx])



# ================================
# vizualizace
# ================================

def plot_predictions(
        data: pd.DataFrame,
        test: pd.DataFrame,
        houldout_preds: pd.Series,
        wf_preds: pd.Series,
        next_pred: float,
        next_date: pd.Timestamp
) -> None:

    # nastavení velikosti plátna
    plt.figure(figsize=(12, 6))
    # omezení časové osy
    plot_data = data[data.index >= "2010-01-01"]

    # formátování čáry s ropou
    plt.plot(plot_data.index, plot_data[TARGET_COL],
             label= "Skutčnost (Brent)",
             color="black",
             linewidth=1.5)
    # oddělovací vertikální čára
    plt.axvline(test.index[0],
                color="grey",
                linestyle="--",
                label="Začátek testovací sady")
    # přidání čáry s naší predikcí
    plt.plot(test.index, houldout_preds,
             label="Predikce",
             color="orange",
             linestyle="-.",
             alpha=0.8)
    # walk forward predikce
    plt.plot(wf_preds.index, wf_preds,
             label="walk forward predikce",
             color="green",
             linewidth=2)
    # přidání červeného bodu na místě predikce
    plt.scatter([next_date], [next_pred],
                color="red",
                s=100,
                zorder=5,
                label=f"Budoucnost ({next_date.strftime("%Y-%m")}): {next_pred:.1f} USD")

    plt.title("Predikce ceny ropy brent (USD/bbl)", fonsize=14)
    plt.ylabel("Cena_usd")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("Predikce_ropy.png", dpi=300)
    plt.show()


def main() -> None:
    # krok 1
    result = fit_and_predict()
    print("Trénovací měsíce:", len(result.train))
    print("Testovácí měsíce:", len(result.test))

    # krok 2
    print("Holdout evaluace")
    evalute_forecast(result.test[TARGET_COL], result.predictions)
    comparison = pd.concat([result.test[TARGET_COL], result.predictions], axis=1)
    comparison.columns = ["actual", "prediction"]
    print("posledních 12 predikcí")
    print(comparison.tail(12).round(3))

    # krok 3
    wf_preds = walk_forward_one_step(result.data, result.feature_cols, TEST_MONTHS)
    wf_actual = result.data.loc[wf_preds.index, TARGET_COL]
    print("walk forward evaluace")
    evalute_forecast(wf_actual, wf_preds)

    # krok 4
    importance = feature_importance_table(result.model, result.feature_cols)
    print("Top 15 příznaků")
    print(importance.head(15).round(4))

    # krok 5
    next_row = make_next_month_feature_row(result.data)
    next_pred = result.model.predict(next_row[result.feature_cols])[0]
    print(f"Předpověď pro {next_row.index[0].strftime("%Y-%m")}: {next_pred:.2f} USD/bbl")

    # krok 6
    plot_predictions(
        data=result.data,
        test=result.test,
        houldout_preds=result.predictions,
        wf_preds=wf_preds,
        next_pred=next_pred,
        next_date=next_row.index[0]
    )

if __name__ == "__main__":
    main()













