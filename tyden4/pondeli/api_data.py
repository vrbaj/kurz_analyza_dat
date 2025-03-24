import requests
import pandas as pd
from io import BytesIO
import json

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
    if "spotřebitelských cen" in datova_sada["vyber"]["nazev"]:
        print(f"{datova_sada['vyber']['nazev']} -"
              f" kód sady: {datova_sada['vyber']['kod']}")