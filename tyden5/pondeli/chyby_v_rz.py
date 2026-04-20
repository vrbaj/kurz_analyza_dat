# Importy
import pandas as pd
from tabulate import tabulate

# Nacteni dat
data = pd.read_csv("umele_rz.csv")

# Prevedeni vsech pismen na velka
data["RZ"] = data["RZ"].apply(lambda x: x.upper())



print(tabulate(data.head(), headers="keys", tablefmt="psql"))