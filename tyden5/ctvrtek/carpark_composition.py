import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1) nahrání souboru s daty
df_raw = pd.read_excel("inputs/auta_cr.xlsx")

# průměrné nájezdy
najezdy = {"OA": 20000, "NA": 50000, "T": 125000, "BS": 80000}
ROKY_PRED = 5
BENZIN_VYLOUCENE_ROKY = [2020, 2021, 2022]

# fitrace platného roku
df = df_raw[pd.to_numeric(df_raw["rok"], errors="coerce").notna()].copy()
df["rok"] = df["rok"].astype(int)

# načteme si verifikované hodnoty
verif = df_raw[pd.to_numeric(df_raw["rok"],errors="coerce").isna() & df_raw["Benzin"].notna()]
benzin_2025_verif = verif["Benzin"].values[0] if len(verif) > 0 else None
nafta_2025_verif = verif["Nafta"].values[0] if len(verif) > 0 else None


# 2)  predikce složení vozového parku
sloupce_parku = [c for c in df.columns if c not in ["rok", "Benzin", "Nafta"]]
# roky co chcemem predikvoat
roky_pred = np.arange(df["rok"].max() + 1, df["rok"].max() + 1 + ROKY_PRED)
X = df[["rok"]]
# tabulka pro uložení predicke
predikce_park = pd.DataFrame({"rok": roky_pred})

print("-> predikce vozového parku")

# predicke pro každou kategorii vozdla
for col in sloupce_parku:
    model = LinearRegression()
    model.fit(X,df[col])
    preds = model.predict(pd.DataFrame({"rok": roky_pred}))
    preds = np.maximum(0, preds).astype(int)
    predikce_park[col] = preds
    r2 = model.score(X, df[col])
    print(f" {col:15s} trend: {model.coef_[0]:+.0f}/rok  R2 = {r2:.3f}")

print("predikvoaný park")
print(predikce_park.to_string(index=False))

# 3) model spotřeby

for kat in ["OA","NA","T","BS"]:
    for palivo in ["benzin", "nafta"]:
        col = f"{kat}_{palivo}"
        if col in df.columns:
            df[f"km_{col}"] = df[col] * najezdy[kat] / 1e9

# názvy sloupců pro model spotřeby
feat_benzin = ["km_OA_benzin", "km_NA_benzin", "km_T_benzin", "km_BS_benzin"]
feat_nafta = ["km_OA_nafta", "km_NA_nafta", "km_T_nafta", "km_BS_nafta"]

# treningová data pro benzín
df_train_benzin = df[~df["rok"].isin(BENZIN_VYLOUCENE_ROKY)]
df
# model pro benzín
model_benzin = LinearRegression(fit_intercept=False)
model_benzin.fit(df_train_benzin[feat_benzin], df_train_benzin["Benzin"])
# model pro naftu
model_nafta = LinearRegression(fit_intercept=False)
model_nafta.fit(df[feat_nafta], df["Nafta"])

# metriky
r2_b = model_benzin.score(df_train_benzin[feat_benzin], df_train_benzin["Benzin"])
r2_n = model_nafta.score(df[feat_nafta], df["Nafta"])

# modelové hodnoty pro hsitorické roky
df["Benzin_model"] = model_benzin.predict(df[feat_benzin])
df["Nafta_model"] = model_nafta.predict(df[feat_nafta])

# výpočet kilometrů pro predikovaný park
for kat in ["OA","NA","T","BS"]:
    for palivo in ["benzin", "nafta"]:
        col = f"{kat}_{palivo}"
        if col in predikce_park.columns:
            predikce_park[f"km_{col}"] = predikce_park[col] * najezdy[kat] / 1e9

# predikovaná spotřeba
predikce_park["Benzin_pred"] = model_benzin.predict(predikce_park[feat_benzin])
predikce_park["Nafta_pred"] = model_nafta.predict(predikce_park[feat_nafta])

print("Predicke spotřeby")
print(predikce_park[["rok","Benzin_pred","Nafta_pred"]].to_string(index=False))
# verifikace, porovnání predickea skutečnosti
if benzin_2025_verif:
    b25 = predikce_park.loc[predikce_park["rok"] == 2025, "Benzin_pred"].values[0]
    n25 = predikce_park.loc[predikce_park["rok"] == 2025, "Nafta_pred"].values[0]
    print("Verifikace")
    print(f"Benzín pred: {b25:.2f}, skut={benzin_2025_verif:.2f}")
    print(f"Nafta pred: {n25:.2f}, skut={nafta_2025_verif:.2f}")


# grafické vyjádření

fig, axes = plt.subplots(1,2)

df_ok = df[~df["rok"].isin(BENZIN_VYLOUCENE_ROKY)]
df_vyloucene = df[df["rok"].isin(BENZIN_VYLOUCENE_ROKY)]

ax = axes[0, 0]
ax.plot(df_ok["rok"], df["Benzin"], "o-",
        color="E67E22",
        linewidth=2,
        markersize=6,
        label="skuecnost")

ax.plot(df_vyloucene["rok"], df_vyloucene["Benzin"], "o",
        color="red",
        markersize=5,
        label="vylouceno z modelu")

ax.plot(df["rok"], df["Benzin_model"], "s--",
        color="e67E22",
        linewidth=1,
        markersize=2,
        alpha=0.5,
        label="Model fit")

roky_all = np.concatenate([["rok"].iloc[-1]], roky_pred)
vals_all = np.concatenate([["Benzin_model"].iloc[-1], predikce_park["Benzin_pred"].values])
ax.plot(roky_all, vals_all, "--")
ax.scatter(roky_pred, predikce_park["Benzin_pred"], label=predikce)

plt.show()

