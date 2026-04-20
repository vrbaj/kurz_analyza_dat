# Import knihoven
import pyodbc
import pandas as pd
from tabulate import tabulate
from pathlib import Path
from matplotlib import pyplot as plt

# Stazeni dat (pokud jiz nejsou ulozena v adresari jako CSV soubor)
def stahni_data():
    # Cesta k souboru s ulozenymi daty
    cesta_data = Path("poruseni_s_vybranymi_cinnostmi.csv")

    # Pokud soubor neexistuje, stahnou se data z databaze a ulozi jako CSV
    # soubor
    if not cesta_data.exists():
        # Konektor na databazi
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=10.2.35.17;"
            "DATABASE=MD2_VSCHT;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        # Nacteni vlastni query
        query_cesta = Path("sql_query", "poruseni_s_vybranymi_cinnostmi.sql")
        query = query_cesta.read_text()
        data_vse = pd.read_sql(query, conn)

        # Ulozeni souboru
        data_vse.to_csv(cesta_data, index=False, encoding="utf-8", sep=";")

    # Data jiz jsou stazena
    else:
        # Nacteni dat primo ze souboru
        data_vse = pd.read_csv(cesta_data, sep=";")

    # Vratit nactena data jako vystup z funkce
    return data_vse

# Nacteni hlavnich dat
data_vse = stahni_data()

# Sjednoceni datovych typu u ciselnych typu na integer (cele cislo)
sloupce_data = ["crecord", "cAuditAction", "ccommodity"]
data_vse[sloupce_data] = data_vse[sloupce_data].astype("Int64", errors="raise")

# Odstraneni duplicit v kombinaci crecord - cAuditAction - ccommodity
# data = data_vse.drop_duplicates(subset=["ccrecord", "cAuditAction", "ccommodity"])
data = data_vse # rozhodli jsme se duplicity zachovat

# Nacteni excelovske tabulky s povolenymi kombinacemi KC a typu zbozi
povolene = pd.read_excel("odhalovani_vad.xlsx", sheet_name="MDX_Commodity x MDx_AuditAction") \
    [["cCommodity", "cAuditAction"]]

# Sjednoceni nazvu sloupce ccommodity
povolene.rename(columns={"cCommodity": "ccommodity"}, inplace=True)

# Sjednoceni datovych typu pro oba sloupce
sloupce_povolene = ["ccommodity", "cAuditAction"]
povolene[sloupce_povolene] = povolene[sloupce_povolene].astype("Int64", errors="raise")

# Levy join tabulky povolene na tabulku data
sparovane_tabulky = data.merge(povolene, on=["cAuditAction", "ccommodity"], how="left", indicator=True)

# Zachovame radky, ktere predstavuji nepovolene kombinace
filtr = sparovane_tabulky["_merge"] == "left_only"
nepovolene = sparovane_tabulky[filtr].copy()
nepovolene.drop(columns=["_merge"], inplace=True)

# Odstraneni radku bez typu zbozi
nepovolene.dropna(inplace=True)

# Odstraneni radku, kde cislo KC neodpovida zadnemu cislu KC v Excelu
filtr = nepovolene["cAuditAction"].isin(povolene["cAuditAction"])
nepovolene = nepovolene[filtr].copy()

# Zobrazeni poctu kontrol pro kazdou z KC, kde je vyplneny neocekavany typ zbozi
nepovolene_pocty = (
    nepovolene.groupby(["cAuditAction", "AuditActionName"])
              .size()
              .sort_values(ascending=False)
              .reset_index(name="pocet")
)

print("#" * 150)
print("Vyskyty kontrolnich cinnosti s neocekavanym typem zbozi")
print(nepovolene_pocty.shape)
print(tabulate(nepovolene_pocty, headers="keys", tablefmt="psql"))

# Nejcasteji se vyskytujici neobvykle kombinace KC a typu zbozi
nepovolene_kombinace = (
    nepovolene.groupby(["cAuditAction", "AuditActionName", "ccommodity", "CommodityName"])
              .size()
              .sort_values(ascending=False)
              .reset_index(name="pocet")
)

print("#" * 150)
print("Nejcastejsi vyskyty neobvyklych kombinaci KC - typ zbozi")
print(tabulate(nepovolene_kombinace, headers="keys", tablefmt="psql"))

# Relativni pocty cinnosti s neobvyklym typem zbozi
# Sloupec s nazvem cinnosti a cislem KC jako indexem
# Pokud bych chtel cetnosti pro jednotlive typy zbozi, staci slucovat pres ccommodity misto cAuditAction
nazvy = data.groupby("cAuditAction")["AuditActionName"].first()

# Sloupec s celkovou cetnosti jednotlivych KC
celkove_pocty = data.groupby("cAuditAction").size().rename("celkem")

# Sloupec s cetnosti neobvyklych typu zbozi pro kazde cislo KC
problematicke = nepovolene.groupby("cAuditAction").size().rename("problematicke")

# Tabulka cetnosti pro KC
relativni_cetnosti = pd.concat([nazvy, celkove_pocty, problematicke], axis=1)

# Vyplneni prazdnych bunek neobvyklych cetnosti pro KC, kde neni zadna neobvykla kombinace
relativni_cetnosti["problematicke"] = relativni_cetnosti["problematicke"].fillna(0)

# Relativni cetnosti vyskytu
relativni_cetnosti["pomer"] = relativni_cetnosti["problematicke"] / relativni_cetnosti["celkem"]
relativni_cetnosti.sort_values("pomer", ascending=False, inplace=True)

print("#" * 150)
print("Tabulka relativnich cetnosti KC")
print(tabulate(relativni_cetnosti, headers="keys", tablefmt="psql"))

# Kontrolni cinnosti, kde neni vyplnen typ zbozi a je ocekavani, ze by mel byt vyplnen
# Filtr, ktery oznacuje radky, kde neni vyplnen typ zbozi a zaroven KC je mezi sledovanymi v excelu
filtr = (data["ccommodity"].isnull()) & (data["cAuditAction"].isin(povolene["cAuditAction"]))
nevyplnene = data[filtr].copy()

# Odfiltrovani vsech KC s cAuditAction 1, 13
nevyplnene = nevyplnene[~nevyplnene["cAuditAction"].isin([1, 13])]

print("#" * 150)
print("Kontroly s nevyplnenym typem zbozi")
print(nevyplnene.shape)
print(tabulate(nevyplnene.head(20), headers="keys", tablefmt="psql"))

# Relativni cetnosti KC, kde neni vyplnen typ zbozi
problematicke = nevyplnene.groupby("cAuditAction").size().rename("problematicke")
relativni_cetnosti = pd.concat([nazvy, celkove_pocty, problematicke], axis=1)
relativni_cetnosti["relativni_pocty"] = relativni_cetnosti["relativni_pocty"].fillna(0)
relativni_cetnosti["pomer"] = relativni_cetnosti["problematicke"] / relativni_cetnosti["celkem"]
relativni_cetnosti.sort_values("pomer", ascending=False, inplace=True)

print("#" * 150)
print("Relativni cetnosti nevyplneneho typu zbozi u jednotlivych KC")
print(tabulate(relativni_cetnosti, headers="keys", tablefmt="psql"))
