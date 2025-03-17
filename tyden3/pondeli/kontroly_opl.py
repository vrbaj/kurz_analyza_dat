# Importy knihoven
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from tabulate import tabulate

# Načtení dat ke kontrolám OPL
data = pd.read_excel("OPL_VSCHT.xlsx", decimal=",")
# Zobrazení prvních pěti řádků tabulky
print(tabulate(data.head(), headers="keys"))
# Zobrazení informací o sloupcích
data.info()
# Základní statistika číselných dat
print(tabulate(data.describe(), headers="keys"))
# Přehled nejčastěji se vyskytujících hodnot ve sloupcích
for sloupec in data.columns:
    # Otestování datového typu
    numericka_data = pd.api.types.is_numeric_dtype(data[sloupec])
    kalendarni_data = pd.api.types.is_datetime64_any_dtype(data[sloupec])
    # Vytvoření objektu pro obrázek
    fig, ax = plt.subplots()
    if numericka_data or kalendarni_data:
        # Zobrazení histogramu hodnot
        sns.histplot(data, x=sloupec, ax=ax, bins=10)
        ax.tick_params(axis="x", labelrotation=90)
        # Uložení názvu sloupce do nadpisu grafu
        ax.set_title(f"Histogram pro {sloupec}")
plt.show()