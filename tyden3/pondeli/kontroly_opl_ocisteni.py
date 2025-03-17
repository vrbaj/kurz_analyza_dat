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
                  "Popis_Mista_Zjisteni", "Kontrola_ID",
                  "Rozkaz_ID", "Typ_Vozidla",
                  "Bydliste_Porusitele"]
data_ocistena = data.drop(columns=mazane_sloupce)
