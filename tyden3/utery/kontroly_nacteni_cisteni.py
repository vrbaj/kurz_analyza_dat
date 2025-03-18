# Importy
import pandas as pd
from tabulate import tabulate
from wordcloud import WordCloud
from matplotlib import pyplot as plt
from unidecode import unidecode

# Načtení dat - načítat excel trvá dlouho, proto jej serializujeme jako pickle
# data_kontroly = pd.read_excel("Kontroly_VSCHT.xlsx")
# data_kontroly.to_pickle("Kontroly_VSCHT.pkl")
data_kontroly = pd.read_pickle("Kontroly_VSCHT.pkl")
# print(tabulate(data_kontroly.head(10), headers="keys"))

# Data info - u několika sloupců se vyskytují prázdné buňky
# data_kontroly.info()

# Data describe - rok narození obsahuje chyby, nebudeme uvažovat
print(tabulate(data_kontroly.describe(), headers="keys"))

# Počty unikátních hodnot v jednotlivých sloupcích
print("Počty unikátních hodnot pro každý sloupec:")
for sloupec in data_kontroly.columns:
    print(f"\t-{sloupec}: {data_kontroly[sloupec].unique().shape[0]}")

# Mapa výskytu slov
# Odstranění bílých znaků a mezer a převedení na malá písmena
seznam_hodnot = data_kontroly["Typ_Vozidla"].apply(
    lambda x: unidecode(f"{x}".strip().replace(" ", "").lower())
    )
seznam_hodnot = list(seznam_hodnot)
wordcloud = WordCloud(collocations=False).generate(", ".join(seznam_hodnot))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
# plt.show()

# Zobrazení okresů
#print(data_kontroly["Okres"].unique())

# Odstranění sloupců s nevyhovujícími hodnotami
sloupce_k_odstraneni = ["Mesto", "Typ_Vozidla", "Rok_narozeni_porusitele", "Okres",
                        "Kontrola_ID", "Rozkaz_ID"]
data_kontroly.drop(columns=sloupce_k_odstraneni, inplace=True)

# Smazání řádků, kde duplicita je ANO
data_kontroly = data_kontroly[data_kontroly["Duplicita"] != "ANO"]
# Smazání sloupce Duplicita - vyskytuje se v něm pouze 1 hodnota
data_kontroly.drop(columns=["Duplicita"], inplace=True)
print(data_kontroly.shape)

# Rozdíly mezi sloupci Stat, Narodnost_Porusitele
data_rozdily = data_kontroly.groupby(["Stat", "Narodnost_Porusitele"]).count()
data_rozdily = data_rozdily.reset_index()
print(data_rozdily[data_rozdily["Narodnost_Porusitele"] == "CZE"])
# Zdá se, že národnost porušitele souhlasí se značkou vozidla
# Pro účely modelování není Národnost podstatná, protože není známá předem
# Odstranění sloupce Nardonost_Porusitele
data_kontroly.drop(columns=["Narodnost_Porusitele"], inplace=True)
# Nahrazení chybějících hodnot ve sloupci Stat
data_kontroly["Stat"] = data_kontroly["Stat"].fillna("neni")
# Zpracování informace o datu a čase
# Vzetí celé hodiny z času
data_kontroly["Cas_Zjisteni"] = data_kontroly["Cas_Zjisteni"].astype(str).apply(lambda x: int(x[:2]))
# Vzetí měsíce v roce a dne v týdnu
data_kontroly["datum_mesic"] = data_kontroly["Datum_Zjisteni"].dt.month
data_kontroly["datum_den_tydne"] = data_kontroly["Datum_Zjisteni"].dt.dayofweek
# Odstranění sloupce Datum_Zjisteni
data_kontroly.drop(columns=["Datum_Zjisteni"], inplace=True)

print(data_kontroly.columns)