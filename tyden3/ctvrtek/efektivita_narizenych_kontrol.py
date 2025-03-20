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
# print("\nČetnosti kombinací Rozkaz_ID a Narizena_Kontrolni_Cinnost")
# print(data_narizene[["Rozkaz_ID", "Narizena_Kontrolni_Cinnost"]].value_counts()
#         .sort_values(ascending=False))

# Zobrazení řádků s Rozkaz_ID 788003 a Narizena_Kontrolni_Cinnost VV - minerální oleje
print("\nŘádky s Rozkaz_ID 788003 a Narizena_Kontrolni_Cinnost VV - minerální oleje")
print(tabulate(data_narizene[(data_narizene["Rozkaz_ID"] == 788003) &
                             (data_narizene["Narizena_Kontrolni_Cinnost"] == "VV - minerální oleje")]
                    .sort_values("NarizenaKC_ID"),
               headers="keys"))

# Zobrazení dat k Rozkaz_ID 788003
print("\n Zobrazení všech dat k rozkazu 788003")
print(tabulate(data_narizene[data_narizene["Rozkaz_ID"] == 788003].sort_values("NarizenaKC_ID"),
               headers="keys"))

"""
Co je hotovo
1) Odstranění dat, jež nejsou k mobilnímu dohledu
2) Odstranění činností, jež nechceme hodnotit
3) Zachování pouze ID rozkazů, jejichž provedené kontroly vedly k porušení

Úprava dat pro porovnávání nařízených a provedených kontrol
1) Tabulka nařízené kontroly
1.a) sloučit Datum_Od s Cas_Vykonu_Od a Datum_Do s Cas_Vykonu_Do pro získání časového rámce nařízení
1.b) zachovat informaci o datech nařízení, o ID rozkazu, o nařízené KČ a o okresu 
2) Tabulka provedené kontroly
2.a) sloučit Datum_Zjisteni s Cas_Zjisteni
2.b) zachovat informaci o datu provedení kontroly, ID rozkazu, provedené KČ a okresu kontroly

Sloučení a porovnání tabulek
1) sloučení podle ID rozkazu a okresu => vzniknou duplicity, protože součástí nařízení je několik
   kontrolních činností na stejném místě v rámci stejného rozkazu
2) sloučenou tabulku je třeba filtrovat porovnáním časů tak, že datum/čas provedení musí být 
   v rozmezí daném rozkazem
2.a) zbývající řádky jsou rozkazy, které vedou na porušení > nemusí sedět nařízená a provedená 
     kontrolní činnost
2.b) řádky, kde nesedí provedená kontrolní činnost s nařízenou lze odfiltrovat porovnáním obou 
     činností > zachovat chceme obě tabulky 
"""