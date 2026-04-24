from pathlib import Path
import json
import pandas as pd
from pydantic import BaseModel, Field
from tqdm import tqdm
from tabulate import tabulate

# Nacteni dat
data = pd.read_csv(Path("Kontroly_MD_poruseni-zbozi.csv"))

#print(data.head())
#print(data.columns)

k_analyze = [
    "TypMista",
    "DruhVozidla",
    "Komodita",
    "MnozstviPoruseni",
    "Jednotka",
    "Poznamka",
]

#print(tabulate(data[k_analyze].head(), headers="keys", tablefmt="psql"))

data = data[k_analyze]

system_prompt = """Jsi datový analytik celní správy.
Tvým úkolem je kontrolovat hlášení hlídek a objevit případné špatné hlášení.
Kontroluj pouze dodané informace, nesnaž se vymýšlet něco navíc. 
Najdi pouze jednoznačně špatné informace.
"""

# vytvoříme funkci k analýze jednoho řádku a převedení na user prompt
def vytvor_uzivatelsky_prompt(row) -> str:
  if pd.isna(row["Poznamka"]):
    row["Poznamka"] = "Bez slovního doplnění"
  if pd.isna(row["DruhVozidla"]):
    row["DruhVozidla"] = "Žádné"
  row["Komodita"] = row["Komodita"].replace("VV - ", "")

  prompt = f"""Zkontroluj následující hlášení:

Místo: {row["TypMista"]}
Druh vozidla: {row["DruhVozidla"]}
Komodita: {row["Komodita"]}
Množství porušení: {row["MnozstviPoruseni"]} {row["Jednotka"]}
Slovní doplnění:
{row["Poznamka"]}
"""
  return prompt

