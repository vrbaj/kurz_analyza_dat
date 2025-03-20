# Importy
import pandas as pd
from time import time
from tabulate import tabulate

# Serializace do pickle
# start = time()
# pd.read_excel("Kontroly_VSCHT.xlsx").to_pickle("Kontroly_VSCHT.pkl")
# pd.read_excel("Narizene_Kontroly_VSCHT.xlsx").to_pickle("Narizene_Kontroly_VSCHT.pkl")
# print(f"{time() - start:.3} s")

# Načtení dat
data_narizene = pd.read_pickle("Narizene_Kontroly_VSCHT.pkl")
data_provedene = pd.read_pickle("Kontroly_VSCHT.pkl")

# Sloupce obou tabulek
print(data_narizene.columns)
print(data_provedene.columns)

# Odstranění KČ, jimiž se nechceme zabývat
kc_k_odstraneni = ["Ostatní činnosti", "Převoz FH a KP", "Asistenční činnost", 24,
                   "Ostatní kompetence (361/2000)", "Kontrola stáčišť", "CRMS", "IZS",
                   "Přepravní povolení", "Metodický dohled GŘC", "Činnost odd. 033",
                   "Obecná bezpečnost výrobků", "ADR", "Zákon o obalech"]
