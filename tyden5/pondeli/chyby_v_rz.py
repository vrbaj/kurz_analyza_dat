# Importy
import pandas as pd
from tabulate import tabulate

# Nacteni dat
data = pd.read_csv("umele_rz.csv")

# Prevedeni vsech pismen na velka
data["RZ"] = data["RZ"].apply(lambda x: x.upper())

# Odstraneni mezer / dalsich znamych nechtenych oddelovacu
data["RZ"] = data["RZ"].apply(lambda x: x.replace(" ", "").replace("-", ""))

# Validace kodu RZ
data["je_validni"] = True

# Kontrola poctu znaku
filtr = (data["RZ"].str.len() < 5) | (data["RZ"].str.len() > 8)
data.loc[filtr, "je_validni"] = False

# Kontrola povolenych znaku
povolene_znaky = set("ABCDEFHIJKLMNPRTUVXYZ0123456789")

print(tabulate(data, headers="keys", tablefmt="psql"))