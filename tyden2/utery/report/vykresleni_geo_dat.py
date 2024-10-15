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
print(data_kontroly.head())

## Upraveni GPS souradnic
data_kontroly["axisx"] = data_kontroly["axisx"].apply(lambda x: float(x.replace(",", ".")))
data_kontroly["axisy"] = data_kontroly["axisy"].apply(lambda x: float(x.replace(",", ".")))

## Vytvoreni sloupce pro usporadanou dvojici souradnic
data_kontroly["zemepisna_poloha"] = list(zip(data_kontroly["axisx"],
                                             data_kontroly["axisy"]))
# Transofrmace souradnic do bodu pro pozdejsi zobrazeni
data_kontroly["zemepisna_poloha"] = data_kontroly["zemepisna_poloha"] \
                                        .apply(lambda x: Point(x))