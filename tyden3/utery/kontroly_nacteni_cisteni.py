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
sloupce_k_odstraneni = ["Mesto", "Typ_Vozidla", "Rok_narozeni_porusitele", "Okres"]
data_kontroly.drop(columns=sloupce_k_odstraneni, inplace=True)

# Smazání řádků, kde duplicita je ANO
data_kontroly = data_kontroly[data_kontroly["Duplicita"] != "ANO"]
# Smazání sloupce Duplicita - vyskytuje se v něm pouze 1 hodnota
data_kontroly.drop(columns=["Duplicita"], inplace=True)
print(data_kontroly.shape)

