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
    o.divrep
FROM inetuser.MDx_Disorder d
JOIN inetuser.MDx_Order o ON d.crecorda = o.crecord;
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
df["hodina"] = df["LocTime"].str.replace(".", ":", regex=False).str.split(":")[0]

# převod textu na číslo, v případě že to nejde tak NaN
df["hodina"] = pd.to_numeric(df["hodina"], errors="coerce")
# kontrola velikost
print(df.shape)
# odstranění NaN hodnot
df.dropna(subset=["hodina"], inplace=True)
# kontrola velikosti
print(df.shape)
