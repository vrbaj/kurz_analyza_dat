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
