import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from matplotlib import pyplot as plt
from tabulate import tabulate

# Definice cesty k souboru s daty o PHM
CESTA_K_PHM = Path("ceny_phm.json")
# Pokud soubor neexistuje, chceme zaslat request, pokud existuje,
# request přeskočíme
soubor_existuje = CESTA_K_PHM.exists()
print(f"Soubor existuje: {soubor_existuje}.")

# Adresa API
url_vybery = "https://data.csu.gov.cz/api/dotaz/v1/data/vybery/"
# Název sady
kod_sady = "CENPHMTT01"
# Finální URL
url_sada = url_vybery + kod_sady
print(url_sada)

if not soubor_existuje:
    print("Ssoubor neexistuje, stahuji z API...")
    r_phm = requests.get(url_sada)
    if r_phm.status_code == 200:
        print(f"Vše dobré!")
        with open(CESTA_K_PHM, "w") as f:
            json.dump(r_phm.json(), f)
    else:
        print(f"Request na databázi selhal: {r_phm.status_code}")

# Načtení dat z JSON
with open(CESTA_K_PHM, "r") as f:
    json_phm = json.load(f)

# Co se v jsonu nachází?
print(type(json_phm))
# Jedná se o slovník, projdeme všechny položky slovníku
print("---------- Informace o stažených datech ----------")
for klic, hodnota in json_phm.items():
    print(f"{klic}: {hodnota}")
# Dimenze jsou 453 týdnů × 2 typy údajů (prům. cena a index) × 3 typy PHM (benzin, nafta, LPG)
# Hodnoty jsou pod klíčem value
# Popisky sloupců a řádků jsou pod klíčem dimension

# Hodnoty ve správném formátu (jako je v DataStatu)
data_phm = np.array(json_phm["value"])
# hodnota -1 se nastaví tak, aby se data vešla do 453 řádků
data_phm = data_phm.reshape(453, -1)
# Indexy řádků - týdny
indexy_radky = list(json_phm["dimension"]["CASTPHM"]["category"]["index"].keys())
# Délka indexu, měla by být 453
print(len(indexy_radky))

# Indexy sloupců - potřeba zkombinovat informaci o indexu/ceně a typu PHM
indexy_typ_uka = list(json_phm["dimension"]["IndicatorType"]["category"]["label"].values())
indexy_typ_phm = list(json_phm["dimension"]["CENPHM"]["category"]["label"].values())
print(indexy_typ_uka)
print(indexy_typ_phm)

# Define MultiIndex levels
index_typ_ukazatele = np.repeat(indexy_typ_uka, len(indexy_typ_phm))  # Repeat for each fuel type
index_typ_paliva = np.tile(indexy_typ_phm, len(indexy_typ_uka))  # Tile across "Cena" and "Index"

# Create MultiIndex
multiindex = pd.MultiIndex.from_arrays([index_typ_ukazatele, index_typ_paliva])

# Pandas dataframe
df_phm = pd.DataFrame(data_phm, columns=multiindex, index=indexy_radky)
df_phm.index = pd.to_datetime("1-" + df_phm.index, format='%w-%Y-W%U')
print(tabulate(df_phm.head(), headers="keys", tablefmt="sql"))

# Navrácení jednoho z typů indexu
# print(tabulate(df_phm.xs("Průměrná cena pohonných hmot (Kč/litr)", axis=1).head(), headers="keys", tablefmt="sql"))

# Uložení dat
df_phm.to_csv("ceny_phm.xlsx")
# Vykreslení Průměrných cen a indexu
fig, axs = plt.subplots(1, 2, figsize=(10, 5))
fig.suptitle("Vývoj cen PHM")
df_phm.xs("Průměrná cena pohonných hmot (Kč/litr)", axis=1).plot(ax=axs[0])
df_phm.xs("Index cen pohonných hmot (%)", axis=1).plot(ax=axs[1])
plt.show()