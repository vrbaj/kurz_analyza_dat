import requests
import pandas as pd
from io import BytesIO
import json

url_katalog = "https://data.csu.gov.cz/api/katalog/v1/vybery"

r = requests.get(url_katalog)
print(f"Status odpovědi: {r.status_code}")
if r.status_code == 200:
    with open("katalog_odpoved.json", "w") as f:
        json.dump(r.json(), f)
else:
    print("Přenos selhal")