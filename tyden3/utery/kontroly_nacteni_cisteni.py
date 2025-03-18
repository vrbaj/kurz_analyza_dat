# Importy
import pandas as pd
from tabulate import tabulate


# Načtení dat - načítat excel trvá dlouho, proto jej serializujeme jako pickle
# data_kontroly = pd.read_excel("Kontroly_VSCHT.xlsx")
# data_kontroly.to_pickle("Kontroly_VSCHT.pkl")
data_kontroly = pd.read_pickle("Kontroly_VSCHT.pkl")
# print(tabulate(data_kontroly.head(10), headers="keys"))

# Data info - u několika sloupců se vyskytují prázdné buňky
# data_kontroly.info()

# Data describe
print(tabulate(data_kontroly.describe(), headers="keys"))

