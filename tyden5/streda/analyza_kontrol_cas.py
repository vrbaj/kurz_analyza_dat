import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import csv
import os

from connection_string import conn_string

query = """
SELECT
    d.recdate,
    d.isCrimact,
    d.cAuditAction,
    d.RUIAN_KOD_OBEC,
    d.LocTime,
    d.LocDate,
    d.crecorda,
    dv.division
FROM inetuser.MDx_Disorder d
JOIN inetuser.MDx_Order o ON d.crecorda = o.crecord
JOIN inetuser.MDx_Division dv ON o.cdiv = dv.cdiv 
"""

# připojení k DB
conn = pyodbc.connect(conn_string)

# vytvoření pd DataFrame s výsledkem query
df = pd.read_sql(query, conn)

# odpojení od db
conn.close()

# kontrola výsledku query
print(df.head())
# zjištění celkového počtu záznamů
print(df.shape)
# informace o sloupcích
print(df.columns)

# převedeme sloupec LocDate na datetime objekt
df["LocDate"] = pd.to_datetime(df["LocDate"])
# převedení datumu na den v týdnu
df["den_v_tydnu"] = df["LocDate"].dt.dayofweek

# pondělí = 0, neděle = 6
print(df["den_v_tydnu"])

# kontrola LocTime
print(df["LocTime"])
# extrakce hodiny ze sloupce LocTime
df["hodina"] = df["LocTime"].str.replace(".", ":", regex=False).str.split(":").str[0]

# převod textu na číslo, v případě že to nejde tak NaN
df["hodina"] = pd.to_numeric(df["hodina"], errors="coerce")
df = df[df["hodina"] < 24]
# kontrola velikost
print(f"Kontrola velikosti před odstranění NaN z hodiny: {df.shape}")
# odstranění NaN hodnot
df.dropna(subset=["hodina"], inplace=True)
# kontrola velikosti
print(f"Kontrola velikosti po odstranění NaN z hodiny: {df.shape}")

# denní směna 7:00 - 19:00
# noční směna 19:00 - 7:00
df["smena"] = df["hodina"].apply(lambda h: "denní" if 7 <= h < 19 else "noční")
# kontrola nového sloupečku "smena"
print(df["smena"].describe())

# sloupeček s příslušným CÚ
print(df["division"].unique())

# seskupení dat podle kraje a hodiny kontroly
pivot = df.groupby(["division", "hodina"]).size().unstack(fill_value=0)
# kontrola seskupení
print(pivot.columns)
print(f"Pivot table velikost {pivot.shape}")
print(pivot.head(10))

pivot_relativni = pivot.div(pivot.sum(axis=1), axis= 0) * 100

pivot_relativni["den_podil"] = pivot_relativni[range(7, 19)].sum(axis=1)
pivot_relativni.sort_values("den_podil", ascending=True, inplace=True)
