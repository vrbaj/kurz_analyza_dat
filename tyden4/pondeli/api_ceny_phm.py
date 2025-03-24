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

