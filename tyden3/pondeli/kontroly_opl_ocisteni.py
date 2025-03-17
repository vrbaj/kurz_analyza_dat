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
print(data_ocistena.shape)
# Smazání řádků s neznámým pohlavím
data_ocistena = data_ocistena[data_ocistena["Pohlavi_porusitele"] != "nezjištěno"]
print(data_ocistena.shape)
# Nahrazení roku narození 2099 za 1999
data_ocistena["Rok_narozeni_porusitele"] = \
    data_ocistena["Rok_narozeni_porusitele"].apply(lambda rok: 1999 if rok == 2099 else rok)
print(data_ocistena[data_ocistena["Rok_narozeni_porusitele"] == 2099].shape)