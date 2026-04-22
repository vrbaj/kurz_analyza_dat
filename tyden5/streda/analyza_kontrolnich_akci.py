import pyodbc
import pandas as pd
from tabulate import tabulate
from pathlib import Path
from matplotlib import pyplot as plt
import seaborn as sns
from connection_string import conn_string

# fuknci pro stahovani dat
def stahni_data(nazev_query):
    # podivat se zda nemame data stazene
    cesta_data = Path(nazev_query).with_suffix(".csv")

    # pokud je mame tak pouzijeme
    if cesta_data.exists():
        data = pd.read_csv(cesta_data)

    # pokud ne tak stahneme
    else:
        conn = pyodbc.connect(conn_string)
        # nacteni SQL dotazu
        query_cesta = Path("sql_query", nazev_query + ".sql")
        query = query_cesta.read_text(encoding="utf-8")

        # stahovani dat
        data = pd.read_sql(query, conn)
        # ulozeni pro dalsi pouziti
        data.to_csv(cesta_data, index=False, encoding="utf-8")
    return data

# nejprve zavolame poprve cimz se stahnou data
data1 = stahni_data("pocty_kc_dle_zjisteni")
print(data1.head())

