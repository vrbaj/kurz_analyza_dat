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

## Slouceni tabulek
data_sloucena = pd.merge(tabulky[0], tabulky[1], on=["id_entity", "vyrobek"], how="outer",
                         suffixes=("_skut", "_vyk"))
# Nahrazeni NaN nulami
data_sloucena.fillna(0, inplace=True)
data_sloucena["vyrobek_zkraceny"] = data_sloucena["vyrobek"].apply(lambda x: x.split(" - ")[0])
# Zmena datoveho typu pro roky na int
seznam_sloupcu = ["2023_skut", "2024_skut", "2023_vyk", "2024_vyk"]
for sloupec in seznam_sloupcu:
    data_sloucena[sloupec] = data_sloucena[sloupec].astype(int)
print(data_sloucena.head(), end="\n\n")

## Vyrobky
vsechny_vyrobky = data_sloucena["vyrobek"].unique()
vsechny_vyrobky_zkracene = data_sloucena["vyrobek_zkraceny"].unique()
# Vypsani seznamu unikatnich vyrobku
print(f"Vsechny vyrobky:\n-\t{('\n-\t').join(vsechny_vyrobky.tolist())}")