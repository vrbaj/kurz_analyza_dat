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


# Barevné kódy pro typy paliv
barvy = {"benzin": "#E67E22", "nafta": "#2C3E50", "elektro": "#27AE60"}
# České popisky paliv pro legendu
paliva_label = {"benzin": "Benzín", "nafta": "Nafta", "elektro": "Elektro"}

# Vytvoření mřížky 2×3 grafů
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle("Predikce vozového parku a spotřeby paliv v ČR",
             fontsize=15, fontweight="bold", y=1.01)

# --- Horní řada: 3 grafy vozového parku (OA, NA, T) ---
for ax, (kat, label) in zip(axes[0], [("OA", "Osobní automobily"),
                                       ("NA", "Nákladní automobily"),
                                       ("T", "Tahače")]):
    for palivo in ["benzin", "nafta", "elektro"]:
        col = f"{kat}_{palivo}"               # název sloupce, např. "OA_benzin"
        barva = barvy[palivo]                  # barva pro dané palivo

        # Historická data – plná čára s body
        ax.plot(df["rok"], df[col], "o-", color=barva, markersize=5,
                linewidth=1.5, label=paliva_label[palivo])

        # Napojení predikce na poslední historický bod
        roky_all = np.concatenate([[df["rok"].iloc[-1]], roky_pred])
        if col in predikce_park.columns:
            vals_all = np.concatenate([[df[col].iloc[-1]], predikce_park[col].values])
        else:
            continue  # pokud sloupec v predikci není, přeskoč

        # Predikce – čárkovaná čára + diamantové body
        ax.plot(roky_all, vals_all, "--", color=barva, linewidth=1.5, alpha=0.5)
        ax.scatter(roky_pred, predikce_park[col], color=barva, s=35, zorder=5,
                   edgecolors="white", linewidths=0.8, marker="D")

    # Modře podbarvená zóna predikce
    ax.axvspan(roky_pred[0] - 0.5, roky_pred[-1] + 0.5, alpha=0.07,
               color="blue", label="Predikce")
    ax.set_title(label, fontsize=12, fontweight="bold")  # nadpis grafu
    ax.set_xlabel("Rok")                                  # popis osy X
    ax.set_ylabel("Počet vozidel")                        # popis osy Y
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))  # celá čísla na ose X
    # Formátování osy Y – mezery v tisících (1 000 000 místo 1000000)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f"{x:,.0f}".replace(",", " ")))
    ax.legend(fontsize=9, framealpha=0.9)                 # legenda

# --- Spodní řada ---

# Oddělení covid/post-covid bodů pro vizualizaci
df_ok = df[~df["rok"].isin(BENZIN_VYLOUCENE_ROKY)]       # roky použité v tréninku
df_vyloucene = df[df["rok"].isin(BENZIN_VYLOUCENE_ROKY)]  # vyloučené roky

# Graf: Spotřeba benzínu
ax = axes[1, 0]
# Skutečné hodnoty – normální roky
ax.plot(df_ok["rok"], df_ok["Benzin"], "o-", color="#E67E22",
        linewidth=2, markersize=6, label="Skutečnost")
# Skutečné hodnoty – vyloučené roky (červeně)
ax.plot(df_vyloucene["rok"], df_vyloucene["Benzin"], "o", color="red",
        markersize=8, markeredgecolor="white", zorder=5, label="Vyloučeno z modelu")
# Modelový fit na historických datech
ax.plot(df["rok"], df["Benzin_model"], "s--", color="#E67E22",
        linewidth=1.5, markersize=5, alpha=0.5, label="Model (fit)")
# Čárkovaná čára predikce napojená na poslední historický bod
roky_all = np.concatenate([[df["rok"].iloc[-1]], roky_pred])
vals_all = np.concatenate([[df["Benzin_model"].iloc[-1]], predikce_park["Benzin_pred"].values])
ax.plot(roky_all, vals_all, "--", color="#E67E22", alpha=0.5, linewidth=1.5)
# Predikční body (diamanty)
ax.scatter(roky_pred, predikce_park["Benzin_pred"], color="#E67E22", s=50,
           zorder=5, edgecolors="white", linewidths=0.8, marker="D", label="Predikce")
# Verifikační bod 2025 (červená hvězda)
if benzin_2025_verif:
    ax.plot(2025, benzin_2025_verif, "*", color="red", markersize=15,
            zorder=6, label="Skutečnost 2025")
ax.axvspan(roky_pred[0] - 0.5, roky_pred[-1] + 0.5, alpha=0.07, color="blue")
ax.set_title(f"Spotřeba benzínu (R²={r2_b:.3f})", fontsize=12, fontweight="bold")
ax.set_xlabel("Rok")
ax.set_ylabel("Spotřeba")
ax.legend(fontsize=8)
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

# Graf: Spotřeba nafty
ax = axes[1, 1]
ax.plot(df["rok"], df["Nafta"], "o-", color="#2C3E50",
        linewidth=2, markersize=6, label="Skutečnost")
ax.plot(df["rok"], df["Nafta_model"], "s--", color="#2C3E50",
        linewidth=1.5, markersize=5, alpha=0.5, label="Model (fit)")
roky_all = np.concatenate([[df["rok"].iloc[-1]], roky_pred])
vals_all = np.concatenate([[df["Nafta_model"].iloc[-1]], predikce_park["Nafta_pred"].values])
ax.plot(roky_all, vals_all, "--", color="#2C3E50", alpha=0.5, linewidth=1.5)
ax.scatter(roky_pred, predikce_park["Nafta_pred"], color="#2C3E50", s=50,
           zorder=5, edgecolors="white", linewidths=0.8, marker="D", label="Predikce")
if nafta_2025_verif:
    ax.plot(2025, nafta_2025_verif, "*", color="red", markersize=15,
            zorder=6, label="Skutečnost 2025")
ax.axvspan(roky_pred[0] - 0.5, roky_pred[-1] + 0.5, alpha=0.07, color="blue")
ax.set_title(f"Spotřeba nafty (R²={r2_n:.3f})", fontsize=12, fontweight="bold")
ax.set_xlabel("Rok")
ax.set_ylabel("Spotřeba")
ax.legend(fontsize=8)
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

# Graf: Autobusy (vozový park)
ax = axes[1, 2]
for palivo, lbl_col in [("benzin", "Benzín"), ("nafta", "Nafta"), ("alektro", "Elektro")]:
    col = f"BS_{palivo}"                      # sloupec autobusy, např. "BS_nafta"
    barva = barvy.get(palivo, barvy.get("elektro"))  # "alektro" mapuje na barvu elektro
    # Historická data
    ax.plot(df["rok"], df[col], "o-", color=barva, markersize=5,
            linewidth=1.5, label=lbl_col)
    # Predikce
    if col in predikce_park.columns:
        roky_all = np.concatenate([[df["rok"].iloc[-1]], roky_pred])
        vals_all = np.concatenate([[df[col].iloc[-1]], predikce_park[col].values])
        ax.plot(roky_all, vals_all, "--", color=barva, linewidth=1.5, alpha=0.5)
        ax.scatter(roky_pred, predikce_park[col], color=barva, s=35, zorder=5,
                   edgecolors="white", linewidths=0.8, marker="D")
ax.axvspan(roky_pred[0] - 0.5, roky_pred[-1] + 0.5, alpha=0.07,
           color="blue", label="Predikce")
ax.set_title("Autobusy", fontsize=12, fontweight="bold")
ax.set_xlabel("Rok")
ax.set_ylabel("Počet vozidel")
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f"{x:,.0f}".replace(",", " ")))
ax.legend(fontsize=9, framealpha=0.9)

# Uložení grafu
plt.tight_layout()                            # automatické rozmístění grafů
plt.savefig("results/predikce_auta.png", dpi=200, bbox_inches="tight")  # uložení do souboru
plt.show()                                    # zobrazení na obrazovce
print("\nGraf uložen.")

