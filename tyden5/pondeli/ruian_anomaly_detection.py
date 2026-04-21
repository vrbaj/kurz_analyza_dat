import pyodbc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.linear_model import LinearRegression
from scipy import stats

import os
import warnings

# potlačí červené hlášky s varováními
warnings.filterwarnings("ignore", category=UserWarning)

# vytvoření složek pro vstupy a výstupy
os.makedirs("vstupy", exist_ok=True)
os.makedirs("vystupy", exist_ok=True)

# informace pro připojení k databázi
CONN_STR = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=(localdb)\\MSSQLLocalDB;"
            "DATABASE=MD2_VSCHT;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

# =========== logaritmicjá regrese ================
def logaritmicka_regrese_top15():
    print(f"{"="*60}")
    print("RUIAN_detekce_anomálií")
    print(f"{"=" * 60}")

    # 1) načtení excelu s názvy obcí
    print("-> Načítání excelu s obcemi")
    # načtení dat  ecelu do dataframu
    df_obec = pd.read_excel("vstupy/spojene_obce.xlsx", usecols=["Id", "Název obce", "Obyvatel celkem"])
    # přejmenování soupců
    df_obec = df_obec.rename(columns={"Id": "Kod_Obce", "Název obce": "Nazev_Obce", "Obyvatel celkem": "Obyvatele"})
    # převod na celá čísla
    df_obec["Kod_Obce"] = df_obec["Kod_Obce"].astype(str).str.replace(r"\.0$", "", regex=True)
    # vyhozeí duplicitních záznamů
    df_obec = df_obec.drop_duplicates(subset=["Kod_Obce"])

    # 2) načtení dat z databáze
    #název souboru do kterého si uložím mezivýsldek
    CACHE_FILE = "vstupy/cache_delikty.csv"

    if os.path.exists(CACHE_FILE):
        print("-> načítání dat z cache")
        # načtení dat z uloženého souboru pokud není připojení k databázi
        df_db = pd.read_csv(CACHE_FILE, dtype={"Kod_Obce": str}, encoding="utf-8")

    else:
        print("-> načítání dat z databáze")
        # přípraprava řipojení do databáze
        conn = pyodbc.connect(CONN_STR)
        query = """
        SELECT
            d.RUIAN_KOD_OBEC AS Kod_Obce,
            a.nAuditAction AS Typ_Poruseni
        FROM inetuser.MDx_Disorder d
        JOIN inetuser.MDx_AuditAction a ON d.cAuditAction = a.cAuditAction
        WHERE d.isCrimact = 1
            AND a.nAuditAction NOT IN ('Dálniční známky', 'Elektronické mýtné')
 
        """

        # bahrání dat z databáze pomocí query do dataframu
        df_db = pd.read_sql(query, conn)
        conn.close()

        # oprava záznamů s .0 na celé čísla
        df_db["Kod_Obce"] = df_db["Kod_Obce"].astype(str).str.replace(r"\.0$", "", regex=True)
        # odstranění záznamů s kodm obce nula
        df_db = df_db[df_db["Kod_Obce"] != "0"]
        # uložení výszupu do databáze
        df_db.to_csv(CACHE_FILE, index=False)

    # 3) propojení dat a přdzpracování
    print("-> sloučení dat a předzpracování")
    # spočtení kolik je dleiktů na obec
    delikty_obce = df_db.groupby("Kod_Obce").size().reset_index(name="Pocet_Deliktu")
    # spojení dat
    df = pd.merge(delikty_obce, df_obec, on="Kod_Obce", how="inner")
    print(df.head())

logaritmicka_regrese_top15()