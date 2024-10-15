# Importy knihoven
import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from shapely.geometry import Point
import geopandas as gpd

# Vykresleni vsech sloupcu
pd.set_option("display.max_columns", None)

## Nacteni dat o celnich kontrolach
cesta_kontroly = Path("Data_kontroly.csv")
data_kontroly = pd.read_csv(cesta_kontroly, sep=";")
# print(data_kontroly.head())

## Upraveni GPS souradnic
data_kontroly["axisx"] = data_kontroly["axisx"].apply(lambda x: float(x.replace(",", ".")))
data_kontroly["axisy"] = data_kontroly["axisy"].apply(lambda x: float(x.replace(",", ".")))

## Vytvoreni sloupce pro usporadanou dvojici souradnic
data_kontroly["zemepisna_poloha"] = list(zip(data_kontroly["axisx"],
                                             data_kontroly["axisy"]))
# Transofrmace souradnic do bodu pro pozdejsi zobrazeni
data_kontroly["zemepisna_poloha"] = data_kontroly["zemepisna_poloha"] \
                                        .apply(lambda x: Point(x))

## Vykresleni lokaci kontrol do mapy
# Nahrani geografickych dat ke krajim CR
cesta_mapa = Path("geojson", "kraje.json")
gdf_mapa = gpd.read_file(cesta_mapa)
kraje = {
    "CZ0100000000": "Hlavní město Praha",
    "CZ0200000000": "Středočeský kraj",
    "CZ0310000000": "Jihočeský kraj",
    "CZ0320000000": "Plzeňský kraj",
    "CZ0410000000": "Karlovarský kraj",
    "CZ0420000000": "Ústecký kraj",
    "CZ0510000000": "Liberecký kraj",
    "CZ0520000000": "Královéhradecký kraj",
    "CZ0530000000": "Pardubický kraj",
    "CZ0630000000": "Kraj Vysočina",
    "CZ0640000000": "Jihomoravský kraj",
    "CZ0710000000": "Olomoucký kraj",
    "CZ0720000000": "Zlínský kraj",
    "CZ0800000000": "Moravskoslezský kraj"
}
print(gdf_mapa.head())