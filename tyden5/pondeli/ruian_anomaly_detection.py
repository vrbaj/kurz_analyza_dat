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
            "SERVER=10.2.35.17;"
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
    # ošetření případu kdy počet obyvatel chybí
    df = df.dropna(subset=["Obyvatele"])
    # odstraněníobcí s málo delikty
    df = df[(df["Obyvatele"] > 0) & (df["Pocet_Deliktu"] >= 5)]


    # 4) loratitmická regrese
    print("-> fitování logaritmické regrese")
    # převod na logarimtickouo škálu
    log_X = np.log10(df["Obyvatele"].values).reshape(-1,1)
    log_Y = np.log10(df["Pocet_Deliktu"].values)

    # definování modelu
    model = LinearRegression()
    # natrénování
    model.fit(log_X, log_Y)
    # zobrazení metriky modelu
    print(f"Metrika modelu: {model.score(log_X, log_Y)}")

    # 5) výpočet očekávané hodnoty a odchylky
    df["Log_Ocekavane"] = model.predict(log_X)
    # převod zpět z logaritmické škály
    df["Ocekavane"] = 10**df["Log_Ocekavane"]
    # výpočet orchylky
    df["Odchylka"] = df["Pocet_Deliktu"] - df["Ocekavane"]
    # seřazení
    extremy = df.sort_values(by="Odchylka", ascending=False)

    # omezení počtu extrémů
    # reorganizace tabulky
    vypis = extremy[["Kod_Obce", "Nazev_Obce", "Obyvatele", "Pocet_Deliktu", "Ocekavane", "Odchylka"]]
    # zaokrouhlení výsledků
    vypis["Ocekavane"] = vypis["Ocekavane"].round(1)
    vypis["Odchylka"] = vypis["Odchylka"].round(1)
    # print(vypis.to_string(index=False))

    # 6) tvorba grafu
    print("-> tvorba grafu")
    # nastavení velikosti plátna
    plt.figure(figsize=(14,9))
    # definování grafu
    plt.scatter(df["Obyvatele"], df["Pocet_Deliktu"], color="#1f77b4", alpha=0.5, edgecolor="black",
                label="Obce (více než 5 deliktů)")
    # plt.show()
    # kreslení regresní křivky
    log_x_range = np.linspace(log_X.min(), log_X.max(), 100).reshape(-1,1)
    log_y_pred = model.predict(log_x_range)
    # převod z logarimtické škály
    x_range = 10 ** log_x_range
    y_pred = 10 ** log_y_pred

    # přidání regresní křivky
    plt.plot(x_range,y_pred, color="red", linewidth=2, label="Regresní křivka")

    # nastavení logarimtické škály
    plt.xscale("log")
    plt.yscale("log")

    # plt.show()
    # přidání popisků
    plt.title("Regrese zlogaritmizovaných dat (15 nevětších anomálií)", fontsize=15)
    plt.xlabel("Počet obyvatel", fontsize=12)
    plt.ylabel("Počet deliktů", fontsize=12)
    plt.grid(True, which="both", ls="--", alpha=0.3)

    # zvíraznění 15 největších anomálií
    top_15 = extremy.head(15)
    # překreslíme 15 bodů v grafu
    plt.scatter(top_15["Obyvatele"], top_15["Pocet_Deliktu"], color="red", s=100, edgecolor="black",
                label="Top 15 anomálií")
    # plt.show()
    # přiřazení názvů obcí bodům
    for _, row in top_15.iterrows():
        plt.annotate(
            row["Nazev_Obce"],
            (row["Obyvatele"], row["Pocet_Deliktu"]),
            xytext=(7,7), textcoords="offset points",
            fontsize=9, fontweight="bold"
        )

    # poslední úpravy grafu
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig("vystupy/graf_odchylek.png")
    plt.show()


logaritmicka_regrese_top15()