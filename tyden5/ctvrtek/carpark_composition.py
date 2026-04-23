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
