# Importy
import pandas as pd
from time import time
from tabulate import tabulate

# Serializace do pickle
# start = time()
# pd.read_excel("Kontroly_VSCHT.xlsx").to_pickle("Kontroly_VSCHT.pkl")
# pd.read_excel("Narizene_Kontroly_VSCHT.xlsx").to_pickle("Narizene_Kontroly_VSCHT.pkl")
# print(f"{time() - start:.3} s")

# Načtení dat
data_narizene = pd.read_pickle("Narizene_Kontroly_VSCHT.pkl")
data_provedene = pd.read_pickle("Kontroly_VSCHT.pkl")

# Sloupce obou tabulek
print(data_narizene.columns)
print(data_provedene.columns)

# KČ, jimiž se nechceme zabývat
kc_k_odstraneni = ["Ostatní činnosti", "Převoz FH a KP", "Asistenční činnost", 24,
                   "Ostatní kompetence (361/2000)", "Kontrola stáčišť", "CRMS", "IZS",
                   "Přepravní povolení", "Metodický dohled GŘC", "Činnost odd. 033",
                   "Obecná bezpečnost výrobků", "ADR", "Zákon o obalech"]

# Velikost tabulky před odstraněním zvolených činností
print("Velikost načtených tabulek: ", data_narizene.shape, data_provedene.shape)

# Odstranění zvolených KČ z obou tabulek
data_narizene = data_narizene[
                    ~data_narizene["Narizena_Kontrolni_Cinnost"].isin(kc_k_odstraneni)
                ]
data_provedene = data_provedene[
                    ~data_provedene["Kontrolni_Cinnost"].isin(kc_k_odstraneni)
                 ]
# Velikost tabulek po odstranění zvolených kontrolních činností
print("Velikost tabulek po odstranění zvolených KČ: ",
      data_narizene.shape, data_provedene.shape)

# Filtrování podle útvaru, budeme pracovat pouze s daty mobilního dohledu
data_narizene = data_narizene[data_narizene["Utvar"] == "Mobilní dohled"]
data_provedene = data_provedene[data_provedene["Utvar"] == "Mobilní dohled"]

# Velikost tabulek po odfiltrování kontrol, kde není mobilní dohled jako útvar
print("Velikost tabulek po filtrování pouze mobilního dohledu: ", data_narizene.shape,
      data_provedene.shape)

# Omezení rozkazů na ty, u nichž provedená kontrola vedla na porušení
rozkazy_s_porusenim = data_provedene[data_provedene["Poruseni"] == "ANO"]
rozkazy_s_porusenim = rozkazy_s_porusenim["Rozkaz_ID"].unique().tolist()
print("Počet ID rozkazů, jejichž kontrolní činnost vede na porušení: ",
      len(rozkazy_s_porusenim))

# Filtrace řádků v obou tabulkách, jejichž rozkazy vedou na porušení
data_provedene = data_provedene[data_provedene["Rozkaz_ID"].isin(rozkazy_s_porusenim)]
data_narizene = data_narizene[data_narizene["Rozkaz_ID"].isin(rozkazy_s_porusenim)]

# Velikost tabulek po odfiltrování rozkazů, jež nevedou na porušení
print("Velikost tabulek po odfiltrování rozkazů bez porušení: ", data_narizene.shape,
      data_provedene.shape)

# Četnost kombinací Rozkaz ID - Nařízená KČ ID
# print("\nTabulka s četnostmi kombinací Rozkaz_ID a NarizenaKC_ID")
# print(data_narizene[["Rozkaz_ID", "NarizenaKC_ID"]].value_counts().sort_index())

# Zobrazení řádků, kde je četnost kombinace vyšší než 1
# print("\nÚdaje pro rozkaz 733689 a KČ ID 1562285")
# print(tabulate(data_narizene[(data_narizene["Rozkaz_ID"] == 733689) &
#                     (data_narizene["NarizenaKC_ID"] == 1562285)], headers="keys"))

# Četnost kombinací Rozkaz ID - Nařízená kontrolní činnost
print("\nČetnosti kombinací Rozkaz_ID a Narizena_Kontrolni_Cinnost")
print(data_narizene[["Rozkaz_ID", "Narizena_Kontrolni_Cinnost"]].value_counts()
        .sort_values(ascending=False))