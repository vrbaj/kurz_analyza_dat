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
povolene_znaky = set("ABCDEFHIJKLMNPRSTUVXYZ0123456789")
data["je_validni"] = data.apply(lambda x: x["je_validni"] if \
            set(x["RZ"]).union(povolene_znaky) == povolene_znaky else False, axis=1)

# Kontrola, ze znacka obsahuje alespon jednu cislici
cislice = set([str(x) for x in range(10)])
data["je_validni"] = data.apply(lambda x: x["je_validni"] if \
            len(set(x["RZ"]).intersection(cislice)) > 0 else False, axis=1)

print("Validni formaty")
print(tabulate(data[data["je_validni"] == True], headers="keys", tablefmt="psql"))

print("Nevhodne formaty")
print(tabulate(data[data["je_validni"] == False], headers="keys", tablefmt="psql"))