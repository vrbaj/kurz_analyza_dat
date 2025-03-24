import requests
import pandas as pd
from io import BytesIO
import json
import numpy as np

# url dotazu ze kterého získáme json
url_katalog = "https://data.csu.gov.cz/api/katalog/v1/vybery"

# zavolání API a přečtení odpovědi
# r = requests.get(url_katalog)
# print(f"Status odpovědi: {r.status_code}")
# if r.status_code == 200:
#     # uložení odpovědi jako json
#     with open("katalog_odpoved.json", "w") as f:
#         json.dump(r.json(), f)
# else:
#     print("Přenos selhal")
with open("katalog_odpoved.json") as f:
    json_katalog = json.load(f)
print(len(json_katalog))
# print(json_katalog)
print(json_katalog[0])
print("-------------Klíčová slova vráceného slovníku--------------")
print(json_katalog[0].keys())
print(json_katalog[0]["vyber"])
print("--------------------------------------------")
print(json_katalog[0]["sada"])
for datova_sada in json_katalog:
    if "Harmonizovaný index spotřebitelských cen (HICP) - měsíční" in datova_sada["vyber"]["nazev"]:
        print(f"{datova_sada['vyber']['nazev']} -"
              f" kód sady: {datova_sada['vyber']['kod']}")
        kod_sady = datova_sada["vyber"]["kod"]
        break
url_vybery = "https://data.csu.gov.cz/api/dotaz/v1/data/vybery/"
url_harmonizovany_index = url_vybery + kod_sady
print(url_harmonizovany_index)

# r_hi = requests.get(url_harmonizovany_index)
# if r_hi.status_code == 200:
#     print(f"Request harmonizoný index odpověď: {r_hi.status_code}")
#     with open("harmonizovany_index.json", "w") as f:
#         json.dump(r_hi.json(), f)
# else:
#     print(f"Request harmonizovaný index selhal: {r_hi.status_code}")
with open("harmonizovany_index.json") as f:
    json_hi = json.load(f)
print(json_hi)
print(json_hi.keys())
print(json_hi["value"])
print("--------Posledních 5 položek VALUE--------")
print(json_hi["value"][-5:])
print("---------Počet hodnot v jsonu-----------")
print(len(json_hi["value"]))
print(len(json_hi["value"]) / 302)
# label, source, note, updated, id, size, role, dimension, extension
print("------ Label ----------")
print(json_hi["label"])  # název výběru
print("------ Source ------")
print(json_hi["source"])
print("--------- Note ----------")
print(json_hi["note"])
print("-------- Updated ---------")
print(json_hi["updated"])  # čas requestu
print("---------- ID ----------")
print(json_hi["id"])
print("------------ Size -----------")
print(json_hi["size"])  # velikost tabulky
print("------------ Role ------------")
print(json_hi["role"])
print("------------ Dimension -----------")
print(json_hi["dimension"])
print(json_hi["dimension"].keys())
print(json_hi["dimension"]["CZCOICOP"])
print("----------- CZCOICOP --------------")
print(json_hi["dimension"]["CZCOICOP"].keys())
print(json_hi["dimension"]["CZCOICOP"]["category"])
print(json_hi["dimension"]["CZCOICOP"]["category"].keys())
print(json_hi["dimension"]["CZCOICOP"]["category"]["label"])
kategorie = json_hi["dimension"]["CZCOICOP"]["category"]["label"].values()
print("-------------- Kategorie ---------------")
print(list(kategorie))
print("-------------- CasM --------------")
print(json_hi["dimension"]["CasM"])
print(json_hi["dimension"]["CasM"].keys())
print(json_hi["dimension"]["CasM"]["category"].keys())
print(json_hi["dimension"]["CasM"]["category"]["index"].keys())
print("------- Sloupečky měsíce ----------")
print(len(json_hi["dimension"]["CasM"]["category"]["index"].keys()))
nazvy_sloupecku = list(json_hi["dimension"]["CasM"]["category"]["index"].keys())
print(nazvy_sloupecku)
pocet_radku = json_hi["size"][3]
pocet_sloupcu = json_hi["size"][4]
hodnoty_tabulky = np.array(json_hi["value"]).reshape(pocet_radku, pocet_sloupcu)
print(hodnoty_tabulky.shape)
print(hodnoty_tabulky)
df = pd.DataFrame(hodnoty_tabulky, columns=nazvy_sloupecku)
print(df.head())
print(df.tail())
kategorie = pd.DataFrame({"kategorie":list(kategorie)})
print(kategorie)
tabulka_ihc = pd.concat([kategorie, df], axis=1)
print(tabulka_ihc.head())