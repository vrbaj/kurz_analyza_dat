# Importy
import requests
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json
from pathlib import Path
from tabulate import tabulate


# Cesta k souboru s PHM
CESTA_K_PHM = Path("ceny_phm.json")
# Pokud soubor neexistuje, tak budeme zasílat request, pokud existuje, tak request
# přeskočíme
soubor_existuje = CESTA_K_PHM.exists()
print(f"Soubor existuje: {soubor_existuje}")

# Adresa API
url_vybery = "https://data.csu.gov.cz/api/dotaz/v1/data/vybery/"
# Název sady
kod_sady = "CENPHMTT01"
# Finální URL
url_sada = url_vybery + kod_sady
print(url_sada)

# Zaslání requestu na API
if not soubor_existuje:
    # Pokud soubor neexistuje
    r_phm = requests.get(url_sada)
    if r_phm.status_code == 200:
        print("Vše dobré!")
        # Uložení výsledku z api do JSON souboru
        with open(CESTA_K_PHM, "w") as f:
            json.dump(r_phm.json(), f)
    else:
        print(f"Request selhal: {r_phm.status_code}")
else:
    print("Soubor již existuje, přeskakuji request.")

# Načtení dat z JSON souboru
with open(CESTA_K_PHM, "r") as f:
    json_phm = json.load(f)
# Jedná se o slovník, projdeme klíče
print("---------- Informace o stažených datech ----------")
for klic, hodnota in json_phm.items():
    print(f"{klic}: {hodnota}")
# Dimenze tabulky je 453 týdnů × 2 typy indexů (cena a index)
# × 3 typy PHM (benzin, nafta, LPG)
# Samotné hodnoty jsou pod klíčem value
# Popisky sloupců a řádků jsou pod klíčem dimension

# Změna dimenzí dat do formátu stejného jako v DataStatu (453 řádků a n sloupců)
data_phm = np.array(json_phm["value"])
# hodnota -1 nastaví druhou dimenzi tak, aby se všechna data vešla do 453 řádků
data_phm = data_phm.reshape(453, -1)
print("-------------------------")
print(data_phm.shape)

# Uložení indexů řádků (týdny)
indexy_radky = list(json_phm["dimension"]["CASTPHM"]["category"]["index"].keys())

# Indexy sloupců
index_typ_ukazatele = list(json_phm["dimension"]["IndicatorType"]["category"]["label"].values())
index_typ_paliva = list(json_phm["dimension"]["CENPHM"]["category"]["label"].values())
print("---------- Indexy sloupců ----------")
print(index_typ_ukazatele)
print(index_typ_paliva)
print(f"Počet řádků: {len(indexy_radky)}")

# Zmnožení sloupců, aby z nich bylo možné vytvořit indexy v DataFrame
# funkce repeat vytvoří pole, kde se za sebou několikrát opakuje každá z vložených hodnot
typ_uka = np.repeat(index_typ_ukazatele, len(index_typ_paliva))
# funkce tile zopakuje pole hodnot a spojí je dohromady
typ_pal = np.tile(index_typ_paliva, len(index_typ_ukazatele))

# MultiIndex
multiindex = pd.MultiIndex.from_arrays([typ_uka, typ_pal])

# Pandas DataFrame
df_phm = pd.DataFrame(data_phm, columns=multiindex, index=indexy_radky)

# Přetvoření indexu (číslo týdne) na časovou známku
df_phm.index = "1-" + df_phm.index
# to_datetime vezme textovou hodnotu a udělá z ní datum
# v argumentu format určuji, kde se objevuje informace o datu v textovém řetězci
# %w - reprezentuje číslo dne v týdnu, %Y reprezentuje rok, %U reprezentuje číslo týdne v roce
df_phm.index = pd.to_datetime(df_phm.index, format="%w-%Y-W%U")

print(tabulate(df_phm.head(), headers="keys"))
