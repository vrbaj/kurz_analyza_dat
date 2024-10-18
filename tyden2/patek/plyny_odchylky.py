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
# Ulozeni sledovanych skupin
kontrolovane_vyrobky = ["271102", "290107", "271151", "271153"]

## Subjekty
seznam_subjektu = data_sloucena["id_entity"].unique().tolist()
# Vypsani seznamu unikatnich subjektu
print(f"Vsechny subjekty:\n-\t{('\n-\t').join(seznam_subjektu)}")

## Vytvoreni rozdilu pro konkretni rok
for rok in [2023, 2024]:
    ## Vykresleni rozdilu mezi skut a vyk u vsech subjektu
    data_rozdil = data_sloucena[["id_entity", "vyrobek", "vyrobek_zkraceny",
                                 f"{rok}_skut", f"{rok}_vyk"]].copy()
    data_rozdil["rozdil"] = data_rozdil[f"{rok}_vyk"] - data_rozdil[f"{rok}_skut"]
    # Barvy
    # barvy = ["crimson" if vyrobek in kontrolovane_vyrobky else "darkblue"
    #          for vyrobek in vsechny_vyrobky_zkracene]
    barvy = []
    for vyrobek in vsechny_vyrobky_zkracene:
        if vyrobek in kontrolovane_vyrobky:
            barvy.append("crimson")
        else:
            barvy.append("darkblue")

    ## Iterace pres jednotlive subjekty pro vykresleni grafu produkci
    for subjekt in seznam_subjektu:
        fig, ax = plt.subplots(figsize=(5, 5))
        # Vytvoreni tabulky, ktera v jednom sloupci obsahuje vsechny cisla skupin vyrobku
        df_vyrobky = pd.DataFrame(data=vsechny_vyrobky_zkracene, columns=["vyrobek_zkraceny"])
        # Vytvoreni tabulky pro subjekt, kde bude produkce VSECH skupin vyrobku
        data_subjekt = df_vyrobky.merge(data_rozdil[data_rozdil["id_entity"] == subjekt],
                                        on="vyrobek_zkraceny", how="left")
        # Nahrazeni chybejicich hodnot nulami
        data_subjekt.fillna(0, inplace=True)
        # U rozdilu chceme mit cele cislo
        data_subjekt["rozdil"] = data_subjekt["rozdil"].astype(int)
        print(data_subjekt, end="\n\n")

        # Vykresleni dat
        sloupce = data_subjekt.plot(kind="bar", x="vyrobek_zkraceny", y="rozdil", color=barvy,
                                    ax=ax)
        # Nazev grafu
        ax.set_title(f"Rozdíl ve výkazech pro {subjekt} v roce {rok}", fontweight="bold")
        # Doplneni popisky pro jednotlive sloupce
        for kontejner in ax.containers:
            ax.bar_label(kontejner)
        # Schovani legendy
        ax.get_legend().set_visible(False)
        # Schovani znacek na ose
        ax.tick_params(axis="both", which="both", length=0)
        # Schovani popisku na y-ove ose
        ax.set_yticks([])
        # Pridani horizontalni cary do hodnoty 0 misto x-ove osy
        ax.hlines(0, -999, 999, color="black", linewidth=1)
        # Schovani ramecku kolem grafu
        for dirs in ["top", "bottom", "left", "right"]:
            ax.spines[dirs].set_visible(False)
        # Nastaveni popisku osy x
        ax.set_xlabel("Skupina výrobků")
        # Ohraniceni kolem celeho obrazku
        fig.patch.set_linewidth(1.5)
        fig.patch.set_edgecolor("black")
        plt.tight_layout()
        fig.savefig(f"{subjekt}_{rok}.png")

plt.show()