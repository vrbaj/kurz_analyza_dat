from pathlib import Path
import json
import pandas as pd
from pydantic import BaseModel, Field
from tqdm import tqdm
from tabulate import tabulate
from litellm import completion

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
Odpověď by měla být co nejkratší.
Nepoužívej formátovací znaky, pouze text. 
Pokud je hlášení v pořádku do pole ok ulož True, pokud ne tak False!
Do pole chyby ulož seznam chyb, pokud nejsou žádné chyby tak nech pole prázdné.
"""

# system prompt
prompt_kontrolora = \
  """Zkontroluj, zda následující kontrola hlášení je fakticky správně.
  Vrať True pokud je kontrola správně, False pokud je kontrola špatně."""

# user prompt pro kontrolora
def vytvor_uzivatelsky_prompt_kontrolora(row, chyby) -> str:
  prompt = f"""Nahlášený chyby:
{chyby}

Kontrolované hlášení:
Místo: {row["TypMista"]}
Druh vozidla: {row["DruhVozidla"]}
Komodita: {row["Komodita"]}
Množství porušení: {row["MnozstviPoruseni"]} {row["Jednotka"]}
Slovní doplnění:
{row["Poznamka"]}"""
  return prompt

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

def zpracuj_odpoved(response) -> dict:
  # odpoved jako str
  odpoved = response.choices[0].message.content
  # odpoved prevedena na objekt strukturovanaodpoved
  odpoved = StrukturovanaOdpoved.model_validate_json(odpoved)
  # prevest na jiny format
  out = {
    "ok": odpoved.ok,
    "chyby": ",".join(odpoved.chyby)
  }
  return out

#print(vytvor_uzivatelsky_prompt(data.iloc[0]))

class StrukturovanaOdpoved(BaseModel):
  ok: bool # True pokud je hlášení v pořádku, False pokud je špatně
  chyby: list[str] # seznam chyb (prázdný pokud je hlášení v pořádku)

mozne_chybne_radky = pd.DataFrame()
pouzite_tokeny = 0

ZPRACUJ = 5
for index, row in tqdm(data.head(ZPRACUJ).iterrows(), total=ZPRACUJ):
  prompt = vytvor_uzivatelsky_prompt(row.to_dict())

  response = completion(
    model="ollama/ministral-3:3b",
    messages = [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": prompt},
    ],
    response_format=StrukturovanaOdpoved,
    api_base = "http://localhost:11434",
  )
  pouzite_tokeny += response.usage.total_tokens

  odpoved = zpracuj_odpoved(response)
  if not odpoved["ok"]:
    print(odpoved["chyby"])
    kontrolor_prompt = vytvor_uzivatelsky_prompt_kontrolora(row, odpoved["chyby"])
    resposnse_kontrolora = completion(
      model="ollama/ministral-3:3b",
      messages=[
        {"role": "system", "content": prompt_kontrolora},
        {"role": "user", "content": kontrolor_prompt},
      ]
    )
    pouzite_tokeny += resposnse_kontrolora.usage.total_tokens
    kontrolor_odpoved = resposnse_kontrolora.choices[0].message.content
    if kontrolor_odpoved.strip().lower() == "false":
      print("Kontrolor potvrdil chybu.")
      row["chyby"] = odpoved["chyby"]
      mozne_chybne_radky = pd.concat([mozne_chybne_radky, row])
    else:
      print("Kontrolor zpochybnil chybu")

mozne_chybne_radky.to_csv("mozne_chybne_radky.csv")
print(f"Použito tokenů: {pouzite_tokeny}")
