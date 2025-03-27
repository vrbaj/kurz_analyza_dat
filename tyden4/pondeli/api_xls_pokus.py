import requests
from io import BytesIO


url_xlsx = "https://data.csu.gov.cz/api/dotaz/v1/data/vybery/CENPHMTT01?format=XLSX"
r = requests.get(url_xlsx)
print(f"status - {r.status_code}")
if r.status_code == 200:
    with open("xlsx.xlsx", "wb") as f:
        f.write(r.content)

