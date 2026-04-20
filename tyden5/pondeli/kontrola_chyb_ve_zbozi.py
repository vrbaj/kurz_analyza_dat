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

print(tabulate(sparovane_tabulky.head(20), headers="keys", tablefmt="psql"))