import openpyxl
import pandas as pd

# potřebujeme převést řádky v excelu na sloupečky v pandas DataFrame
tabulka_jmeno = "vyvoj_cen_jidlo.xlsx"
# načtení sešitu
sesit = openpyxl.load_workbook(tabulka_jmeno)
# výběr listu DATA
list_data = sesit["DATA"]
# specififkace rozsahu buněk s tabulkou dat
rozsah_bunek = list_data["C7:BK106"]
nazvy_sloupcu = []
data = []
# extrakce číselných hodnot a názvů sloupečků pro novou tabulku
for radek in rozsah_bunek:
    data_radku = [bunka.value for bunka in radek[1:]]
    nazvy_sloupcu.append(radek[0].value)
    data.append(data_radku)
print(data)
print(nazvy_sloupcu)
# vytvoření pandas DataFrame
df = pd.DataFrame(data)
print(df.head())
# převedení řádků na sloupce
df = df.transpose()
print(df.head())
# specifikace názvů sloupců pomocí názvů potravin
df.columns = nazvy_sloupcu
df.reset_index(drop=True, inplace=True)
# výběr názvů měsíců/roků
rozsah_bunek = list_data["D6:BK6"]
datum = [bunka.value for bunka in rozsah_bunek[0]]
df["datum"] = datum
# změna datumu na index tabulky
df.set_index("datum", inplace=True)
print(df.head())
# uložení do excelu
df.to_excel("vyvoj_cen_jidlo_upraveno.xlsx")