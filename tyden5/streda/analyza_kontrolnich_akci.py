import pyodbc
import pandas as pd
from tabulate import tabulate
from pathlib import Path
from matplotlib import pyplot as plt
import seaborn as sns

# fuknci pro stahovani dat
def stahni_data(nazev_query):
    # podivat se zda nemame data stazene
    cesta_data = Path(nazev_query).with_suffix(".csv")

    # pokud je mame tak pouzijeme
    if cesta_data.exists():
        data = pd.read_csv(cesta_data)

    # pokud ne tak stahneme
    else:
        conn_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            r"SERVER=(localdb)\MSSQLLocalDB;"
            "DATABASE=MD2_VSCHT;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=no;"
        )
        conn = pyodbc.connect(conn_string)
