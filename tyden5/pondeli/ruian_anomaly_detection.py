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
    df_obec = pd.read_excel("vstupy/spojene_obce.xlsx", usecols=["Id", "Název obce", "Obyvatel celkem"])
    print(df_obec)



logaritmicka_regrese_top15()