# Importy knihoven
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from tabulate import tabulate

# Načtení dat ke kontrolám OPL
data = pd.read_excel("OPL_VSCHT.xlsx", decimal=",")
# Smazání nevyhovujících sloupců
mazane_sloupce = ["Duplicita", "Kontrolni_Cinnost", "Mesto",
                  "Km", "Cas_Zjisteni", "CisloTydne",
                  "Popis_Mista_Zjisteni",
                  "Rozkaz_ID", "Typ_Vozidla",
                  "Bydliste_Porusitele"]
data_ocistena = data.drop(columns=mazane_sloupce)
# print(data_ocistena.shape)
# Smazání řádků s neznámým pohlavím
data_ocistena = data_ocistena[data_ocistena["Pohlavi_porusitele"] != "nezjištěno"]
# print(data_ocistena.shape)
# Nahrazení roku narození 2099 za 1999
data_ocistena["Rok_narozeni_porusitele"] = \
    data_ocistena["Rok_narozeni_porusitele"].apply(lambda rok: 1999 if rok == 2099 else rok)
print(data_ocistena[data_ocistena["Rok_narozeni_porusitele"] == 2099].shape)
# Odstranění řádků s prázdnými buňkami - nebudeme dělat
# data_ocistena.dropna(inplace=True)
# Nalezeni radku, kde chybi narodnost, stat a druh vozidla
# Součet prázdných buněk v každém řádku tabulky
prazdne_bunky_radky = pd.isna(data_ocistena[["Druh_vozidla", "Stat", "Narodnost_Porusitele"]]).sum(axis=1)
# Porovnání, kde počet prázdných buněk na řádku je roven 3
maska = prazdne_bunky_radky == 3
# Vrácení ID Kontroly pro tyto řádky
# print(data_ocistena[maska]["Kontrola_ID"])
# Uložení problematických řádků do excelu
data_ocistena[maska].to_csv("problematicke_id_kontroly.csv", index=False)
# Rozdělení dat podle druhu OPL
druhy_opl = data_ocistena["Druh_OPL"].unique()
print(druhy_opl)
# Množství zadržených OPL
fig, axs = plt.subplots(2, 7, figsize=(25, 10))
axs = axs.reshape(-1)

for i, opl in enumerate(druhy_opl):
    # Filtrace daných OPL s nenulovým zadrženým množstvím
    data_pro_opl = data_ocistena[(data_ocistena["Druh_OPL"] == opl) &
                                 (data_ocistena["Mnoz_v_Porušení"] > 0)]
    # Zobrazení pomocí grafu
    sns.histplot(data_pro_opl, x="Mnoz_v_Porušení", ax=axs[i])
    axs[i].set_title(f"Histogram zadrženého množství pro {opl}")

plt.tight_layout()
plt.show()
