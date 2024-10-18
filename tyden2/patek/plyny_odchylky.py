from matplotlib import pyplot as plt
import json
import pandas as pd
pd.set_option("display.width", 10000)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)

## Nacteni dat
soubor = "Dataset MO.xlsx"
sheety = ["Data EMCS", "Data VSD"]
tabulky = []

# Iterace skrz listy, nacteni tabulky a uprava tabulky
for sheet in sheety:
    # Nahrani tabulky do seznamu
    tabulky.append(pd.read_excel(soubor, sheet))
    ## Uprava sloupcu
    # Prejmenovani
    tabulky[-1].columns = ["id_entity", "vyrobek", "jednotka", "2023", "2024"]
    # Prevod na stejne jednotky a odstraneni sloupce s jednotkami
    if sheet == "Data VSD":
        # Prevedeni produkce z tun na kilogramy
        tabulky[-1][["2023", "2024"]] = tabulky[-1][["2023", "2024"]] * 1000
    # Odstraneni sloupce jednotky
    tabulky[-1].drop("jednotka", axis=1, inplace=True)
    # Odstraneni mezer ze sloupce id_entity
    tabulky[-1]["id_entity"] = tabulky[-1]["id_entity"].str.replace(" ", "")
    print(tabulky[-1].head(), end="\n\n")