# Importy knihoven
import pandas as pd
import geopandas as gpd
from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from shapely.geometry import Point

# Vykresleni vsech sloupcu
pd.set_option("display.max_columns", None)

## Nacteni dat o celnich kontrolach
cesta_kontroly = Path("Data_kontroly.csv")
data_kontroly = pd.read_csv(cesta_kontroly, sep=";")
print(data_kontroly.head())

## Chybejici hodnoty
print(data_kontroly.isna().sum())

## Celkova velikost datasetu
print(data_kontroly.shape)

## Upraveni GPS souradnic
data_kontroly["axisx"] = data_kontroly["axisx"].apply(lambda x: float(x.replace(",", ".")))
data_kontroly["axisy"] = data_kontroly["axisy"].apply(lambda x: float(x.replace(",", ".")))

## Vytvoreni sloupce pro usporadanou dvojici souradnic
data_kontroly["zemepisna_poloha"] = list(zip(data_kontroly["axisx"],
                                             data_kontroly["axisy"]))
# Transofrmace souradnic do bodu pro pozdejsi zobrazeni
data_kontroly["zemepisna_poloha"] = data_kontroly["zemepisna_poloha"] \
                                        .apply(lambda x: Point(x))

## Vraceni radku s nevyplnenym ID vozidla
print("Chybejici ID vozidla")
print(data_kontroly[data_kontroly["ID_vozidla"].isna()])

## Nalezeni casoveho obdobi dat
print("\n----Casove obdobi----")
casove_obdobi_od = data_kontroly["LocDate"].min()
casove_obdobi_do = data_kontroly["LocDate"].max()
print(f"Kontroly probihaly v obdobi od {casove_obdobi_od} do {casove_obdobi_do}.")

## Statistika pokut
print("\n----Statistika pokut----")
statistika_pokuty = data_kontroly[["penalty", "NotCashPenalty", "CashPenalty",
                                   "CashLessPenalty"]].describe()
print(statistika_pokuty)

# Statistika pokut pro kontroly, kde pokuta byla udelena
statistika_udelene_pokuty = data_kontroly[data_kontroly["penalty"] > 0][["penalty"]] \
                                .describe()
print("")
print(statistika_udelene_pokuty)

print("\n----Celkova vyse udelenych pokut---")
print(f"{data_kontroly["penalty"].sum():,}")

## Kontrola, jestli neni v tabulce duplicita podle ID vozidla (melo by byt unikatni)
print("\n----Pocet kontrol na kazde ID vozidla----")
pocty_kontrol_na_vozidlo = (data_kontroly["ID_vozidla"].value_counts()
                                .sort_values(ascending=False))
print(pocty_kontrol_na_vozidlo)

## Kontroly podle kodu zeme
# Pocty kontrol podle kodu zemi
kody_kontroly = data_kontroly["kod"].value_counts().reset_index()
kody_kontroly.columns = ["kod", "pocet"]

# Diskriminujeme ceska auta a auta, ktera nejsou z deseti nejcastejsich zemi
kody_kontroly = kody_kontroly[kody_kontroly["kod"] != "CZ"]
kody_kontroly = kody_kontroly.sort_values("pocet", ascending=False).reset_index(drop=True)
kody_kontroly = kody_kontroly.head(10)
fig, ax = plt.subplots(figsize=(10, 10))
kody_kontroly.plot(ax=ax, x="kod", y="pocet", kind="bar")

# Soucty udelenych pokut podle kodu zeme
kody_kontroly_sumy = data_kontroly.groupby("kod")["penalty"].sum().reset_index()
kody_kontroly_sumy.columns = ["kod", "soucet"]
kody_kontroly_sumy = kody_kontroly_sumy.sort_values("soucet", ascending=False)
kody_kontroly_sumy.plot(x="kod", y="soucet", kind="bar")

## Mezirocni zmeny v poctu provedenych kontrol
# Odstraneni casu z data
data_kontroly["LocDate"] = data_kontroly["LocDate"].apply(lambda x: x.split(" ")[0])
data_kontroly["LocDate"] = pd.to_datetime(data_kontroly["LocDate"])
# Ulozeni informace o roce a mesici z datetime
data_kontroly["rok"] = data_kontroly["LocDate"].dt.year
data_kontroly["mesic"] = data_kontroly["LocDate"].dt.month
# Odfiltrovani dat z roku 2024 a ceskych kontrol
mezirocni_zmeny = data_kontroly[(data_kontroly["rok"] != 2024) &
                                (data_kontroly["kod"] != "CZ")].copy()
# Seskupeni podle roku a mesice, nalezeni poctu pro kazdou kombinaci
mezirocni_zmeny = mezirocni_zmeny.groupby(["rok", "mesic"]).size().reset_index()
# Vytvoreni kontingencni tabulky, kde roky jsou ve sloupcich a mesice v radcich
mezirocni_zmeny_kontab = mezirocni_zmeny.pivot(index="mesic", columns="rok",
                                               values=0)
# Relativni zmena poctu kontrol oproti roku 2022
mezirocni_zmeny_kontab["mezirocni_zmena"] = (mezirocni_zmeny_kontab.iloc[:, 1] -
                                            mezirocni_zmeny_kontab.iloc[:, 0]) / \
                                            mezirocni_zmeny_kontab.iloc[:, 0]
print("\n----Kontingencni tabulka----")
print(mezirocni_zmeny_kontab)
fig, ax = plt.subplots(figsize=(10, 10))
mezirocni_zmeny_kontab.reset_index().plot(ax=ax, x="mesic", y="mezirocni_zmena", kind="bar")
plt.show()
