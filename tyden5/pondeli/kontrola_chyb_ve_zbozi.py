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

print(tabulate(data_vse.head(), headers="keys", tablefmt="psql"))