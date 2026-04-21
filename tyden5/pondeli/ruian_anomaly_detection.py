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


def analyza_patecni_pokles():
    # 1) nahrání dat z databáze
    # cesta k souboru
    CACHE_FILE_KONTROLY = "vstupy/cachce_kontroly.csv"

    if os.path.exists(CACHE_FILE_KONTROLY):
        print("-> nahrávám data z uloženého csv")
        # načítání dat
        df = pd.read_csv(CACHE_FILE_KONTROLY, dtype={"RUIAN_KOD_OBEC":str,"crecorda":str}, encoding="utf-8")

    # funkce pro stahování dat z databáze
    else:
        print("-> stahování dat z databáze")
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
        conn = pyodbc.connect(CONN_STR)
        df = pd.read_sql(query, conn)
        conn.close()

        # uložení do csv souboru
        df.to_csv(CACHE_FILE_KONTROLY, index=False)

    # 2) předzpracování
    print("-> předzpracování")
    # převod datumu ze stringu na datetime format
    df["LocDate"] = pd.to_datetime(df["LocDate"], format="mixed")
    # převod dnů v týdnu
    df["den_v_tydnu"] = df["LocDate"].dt.dayofweek
    # sjeddnocení času
    df["hodina"] = df["LocTime"].str.replace(".", ":", regex=False).str.split(":").str[0]
    df["hodina"] = pd.to_numeric(df["hodina"], errors="coerce")

    # odstranění řádků s neplatnými záznamy
    df =df.dropna(subset=["hodina"])
    print(df)
    # převod na celé čísla
    df["hodina"] = df["hodina"].astype(int)

    # třízení záznamů na denní a noční směnu
    df["smena"] = df["hodina"].apply(lambda h: "denni" if 6 <= h < 18 else "nocni")

    # převod názvů CU
    df["kraj"] = (
        df["divrep"].astype(str)    # převod na string
        .str.split("/").str[0]      # extrakce za lomítkem
        .str.split(",").str[0]      # extrakce za čárkou
        .str.strip()                # odstranění mezer na začátku a konci
    )

    # odstranění záznamů s čísly
    df = df[~df["kraj"].str.match(r"^\d+$")]
    print(df.kraj.value_counts())
    # 3) tvorba heatmapy
    print("-> generování heatmapy")
    # vyopčtení matice kombinací kraj a hodina
    pivot = df.groupby(["kraj", "hodina"]).size().unstack(fill_value=0)
    # kontrola chabějících hodin
    pivot = pivot.reindex(columns=range(24), fill_value=0)
    # převod absolutních hodnot an procentuální vyjádření
    pivot_pct = pivot.div(pivot.sum(axis=1),axis=0)*100
    pivot_pct["den_podil"] = pivot_pct[range(6,18)].sum(axis=1)
    # seřazení krajů
    pivot_pct = pivot_pct.sort_values("den_podil", ascending=True)
    # odstranění pomocného sloupce
    pivot_pct = pivot_pct.drop(columns="den_podil")

    # definice grafu
    fig1, ax1 = plt.subplots(figsize=(16, max(8, len(pivot_pct) * 0.5)))
    im = ax1.imshow(pivot_pct.values, aspect="auto", cmap="YlOrRd", norm=mcolors.PowerNorm(gamma=0.7))

    # pozice popisků, jednotky a popisky
    ax1.set_xticks(range(24))
    ax1.set_xticklabels([f"{h}:00" for h in range(24)], rotation=45, fontsize=9)
    # nastavení popisků na ose y
    ax1.set_yticks(range(len(pivot_pct)))
    ax1.set_yticklabels(pivot_pct.index, fontsize=9)

    ax1.set_xlabel("Hodina", fontsize=12)
    ax1.set_title("Rozložení kontrol v průběhu dne podle krajů", fontsize=14)

    # přidání bílých čar na hranici denní a noční směny
    ax1.axvline(x=5.5, color="white", linewidth=2, linestyle="--", label="6:00 - začátek denní")
    ax1.axvline(x=17.5, color="white", linewidth=2, linestyle="--", label="18:00 - začátek noční")

    # přidání legendy
    ax1.legend(loc="upper right", fontsize=9)
    # barevá škála
    cbar= plt.colorbar(im, ax=ax1, shrink=0.8)
    cbar.set_label("% kontrol", fontsize=10)
    plt.tight_layout()
    fig1.savefig("vystupy/graf_denni.png")
    plt.show()


    # 4) funkce pro statistické testování pátku
    print("-> statistické testy")

    def testuj_patek(data):
        # spočítání denních kontrol
        kontroly = data.groupby(["LocDate", "den_v_tydnu"]).size().reset_index(name="pocet")
        pracovni = kontroly[kontroly["den_v_tydnu"] <= 4]
        patek = pracovni[pracovni["den_v_tydnu"] == 4]["pocet"]
        po_ct = pracovni[pracovni["den_v_tydnu"] <=3]["pocet"]

        # odstranění vzorků s méně než 5 pozorováními
        if len(patek) <5 or len(po_ct) <5:
            # vrátí None, nepužijem tento kraj, nebo směnu
            return None
        # welchuv test
        t_stat, p_two = stats.ttest_ind(patek, po_ct, equal_var=False)
        p_one = p_two / 2
        # Mann-whitney U test
        _, p_mw = stats.mannwhitneyu(patek, po_ct, alternative="less")
        # cohenovo d
        pooled_std = ((po_ct.std() ** 2 + patek.std() ** 2)/2) ** 0.5
        cohen_d = (po_ct.mean()-patek.mean()) / pooled_std if pooled_std > 0 else 0
        signif = "ANO" if (t_stat < 0 and p_one < 0.05) else "NE"

        return(
            round(po_ct.mean(),1),
            round(patek.mean(),1),
            round(po_ct.mean() - patek.mean(),1),
            round((po_ct.mean()-patek.mean())/ po_ct.mean() * 100,1),
            round(p_one, 4),
            round(p_mw, 4),
            round(cohen_d, 4),
            signif
        )

    rows = []

    def zpracuj(data, nazev):
        for smena in ["celkem", "denni", "nocni"]:
            subset = data if smena == "celkem" else data[data["smena"] == smena]
            res = testuj_patek(subset)

            if res:
                rows.append((nazev, smena, *res))

    # neprjme spočítám statistku pro celou čr
    zpracuj(df, "ČR CELKEM")
    # teď postupně por každý kraj
    for kraj in sorted(df["kraj"].unique()):
        zpracuj(df[df["kraj"] == kraj], kraj)

    print("hotovo")




# logaritmicka_regrese_top15()
analyza_patecni_pokles()