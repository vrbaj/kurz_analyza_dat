from pathlib import Path
import json
import pandas as pd
from pydantic import BaseModel, Field
from tqdm import tqdm
from tabulate import tabulate

# Nacteni dat
data = pd.read_csv(Path("Kontroly_MD_poruseni-zbozi.csv"))

print(data.head())
print(data.columns)

k_analyze = [
    "TypMista",
    "DruhVozidla",
    "Komodita",
    "MnozstviPoruseni",
    "Jednotka",
    "Poznamka",
]

print(tabulate(data[k_analyze].head(), headers="keys", tablefmt="psql"))