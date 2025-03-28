import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from tabulate import tabulate
from matplotlib import pyplot as plt

# specifikace komodit
id_komodit = ["ropa-brent", "benzin-cz", "motorova-nafta"]
komodity_url = ";".join(id_komodit)

# časové rozlišení dat
od = "2005-01-01"
do = datetime.now().strftime("%Y-%m-%d")
data_url = f"{od.replace('-', '')}-{do.replace('-','')}"

# cesta k souboru s jsonem
cesta_k_souboru = Path(f"kurzy_cz_komodity_{do}.json")
cesta_neexistuje = not cesta_k_souboru.exists()
mena = "czk"
if cesta_neexistuje:
    print(f"Soubor {cesta_k_souboru.name} neexistuje, stahuji data.")
    url = (f"https://data.kurzy.cz/json/komodity/"
           f"id[{komodity_url}]"
           f"mena[{mena}]"
           f"den[{data_url}].json")
    print(f"URL: {url}")
    # stažení dat
    r = requests.get(url)
    if r.status_code == 200:
        with open(cesta_k_souboru, "w") as f:
            json.dump(r.json(), f)
    else:
        print(f"Request selhal, kód: {r.status_code}")
        raise "Skript ukončen, data nestažena"
else:
    print(f"Soubor {cesta_k_souboru.name} existuje")
    with open(cesta_k_souboru, "r") as f:
        data_json = json.load(f)
    print(type(data_json))
    # data jsou seznam
    # print(data_json[0])
    # seznam obsahuje slovníky
    print(type(data_json[0]))
    # položky slovníku
    print(data_json[0].keys())
    print("--------- Položky slovníky - hodnoty -----------")
    for klic, hodnota in data_json[0].items():
        print(f"{klic} - {hodnota}")

    seznam_tabulek = []
    for data_komodita in data_json:
        seznam_tabulek.append(pd.json_normalize(data_komodita["data"]))
        # print(seznam_tabulek[0].columns)
        # print(seznam_tabulek[0].head())
        # změníme sloupec den na datum
        seznam_tabulek[-1]["den"] = pd.to_datetime(seznam_tabulek[-1]["den"])
        # vytvoření index pro sloučení tabulek
        seznam_tabulek[-1].set_index("den", inplace=True)
        # zbavíme se sloupečku mena
        seznam_tabulek[-1].drop(columns=["mena"], inplace=True)
        nazev_komodity = data_komodita["nazev"]
        seznam_tabulek[-1].rename(columns={"hodnota": nazev_komodity}, inplace=True)
        print(seznam_tabulek[-1].columns)
    # sloučení tabulek
    data_df = pd.concat(seznam_tabulek, axis=1)
    print("------------ Info o sloučené tabulce ---------------")
    print(data_df.info())
    # pozor, chybí ceny ropy Brent
    print("----- Počet chybějících hodnot ---------")
    print(tabulate(pd.isna(data_df).sum().reset_index(), headers="keys"))
    # vytiskneme si řádky s chybějící
    print("-------- Řádky s chybějící hodnotou ----------")
    print(tabulate(data_df[pd.isna(data_df["Benzín CZ"])].head(20)))

    # vykreslení dat
    data_df.plot(subplots=True)
    plt.show()

    # interpolace
    data_df = data_df.interpolate()
    print("---------- Chybějící data po interpolaci ----------")
    print(tabulate(pd.isna(data_df).sum().reset_index(), headers="keys"))
    # zpětné vyplnění
    data_df["Ropa Brent"] = data_df["Ropa Brent"].bfill()
    print("---------- Chybějící data po zpětném vyplnění ----------")
    print(tabulate(pd.isna(data_df).sum().reset_index(), headers="keys"))

