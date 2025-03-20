import pandas
import geopandas
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib

# Nacteme data
df = pandas.read_excel("OPL_VSCHT.xlsx", decimal=",")
# Vypiseme si sloupce tabulky
print(df.columns)

# Zbavime se nepotrebnych sloupcu
df = df.drop(columns=["Kraj_zjisteni_poruseni","Okres_zjisteni_poruseni",
                      "Bydliste_Porusitele","Narodnost_Porusitele","Typ_Vozidla",
                      "Rozkaz_ID","Popis_Mista_Zjisteni","CisloTydne",
                      "Km","Mesto","Kontrolni_Cinnost", "Duplicita","Utvar"])

# Zobrazime unikatni hodnoty
for col in df.columns:
    # nebudeme zobrazovat nasledujici sloupce
    if col in ["Cas_Zjisteni","OsaX", "OsaY","OsaX_txt","OsaY_txt"]:
        continue
    print("#"*50) # oddelovac
    print(col, ": ", df[col].unique())

# #Rok_narozeni_porusitele
# df_pracovni = df[df["Rok_narozeni_porusitele"]>1900]
# df_pracovni["Rok_narozeni_porusitele"] = \
#     df_pracovni["Rok_narozeni_porusitele"].apply(
#         lambda x: 1999 if x == 2099 else x)
# sns.histplot(df_pracovni, x="Rok_narozeni_porusitele")
# plt.show()

# print("Jsou OsaX a OsaX_txt stejne?")
# print(df.shape)
# print(df[df["OsaX"]!= df["OsaX_txt"]].shape)
# print(df[df["OsaY"]!= df["OsaY_txt"]].shape)

df = df.drop(columns=["Rok_narozeni_porusitele","OsaX_txt","OsaY_txt"])

# Zbavime se Ruzyně
df = df[df["Celni_Urad"]!= "CÚ Praha Ruzyně"]
df = df.drop(columns=["Celni_Urad"])

# Abychom neměli příliš dimenzionální data, tak zjistíme, 
# které státy jsou nejčastější a ostatní přejmenujeme na "Ostatní"
df["Stat"] = df["Stat"].fillna("Neznamy")
top_staty = df["Stat"].value_counts()
top_staty = top_staty[top_staty>20].index
print(top_staty)
df.loc[~df["Stat"].isin(top_staty),"Stat"] = "Ostatni"
print(df["Stat"].unique())

print(df.columns)
print(df["Misto_kontoly"].value_counts())
df.loc[df["Misto_kontoly"]=="stánek","Misto_kontoly"] = "provozovna"
df.loc[df["Misto_kontoly"]=="domovní prohlídka", "Misto_kontoly"] = "ostatní" 
print(df["Misto_kontoly"].value_counts())


# Zabava s tim jak jsou zapisovana mnozstvi
# for druh in df["Druh_OPL"].unique():
#     jednotky = df[df["Druh_OPL"]==druh]["Merna_jednotka"].unique()
#     #print(druh,": ", jednotky)
#     fig, axs = plt.subplots(1,jednotky.shape[0])
#     if jednotky.shape[0] == 1:
#         axs = [axs]
#     for i, jednotka in enumerate(jednotky):
#         aktualni = df[(df["Druh_OPL"]==druh) & 
#                       (df["Merna_jednotka"]==jednotka)]
#         sns.histplot(aktualni, x="Mnoz_v_Porušení", ax=axs[i])
#         axs[i].set_title(jednotka)
#     fig.suptitle(druh)
#     plt.tight_layout()
# plt.show()

print(df[(df["Druh_OPL"]=="Konopí (sušina - marihuana)")& (df["Merna_jednotka"])=="l" ])

print(df.columns)

# Datum_Zjisteni -> den v tydnu
df["den_v_tydnu"] = df["Datum_Zjisteni"].dt.dayofweek
df = df.drop(columns=["Datum_Zjisteni"])

# Druh_vozidla
df["Druh_vozidla"] = df["Druh_vozidla"].fillna("není")

# Cas_Zjisteni
df["Cas_Zjisteni"] = df["Cas_Zjisteni"].apply(lambda x: int(str(x)[:2]))


# Pohlavi_porusitele
df["Pohlavi_porusitele"] = df["Pohlavi_porusitele"].fillna("nezjištěno")

for col in df.columns:
    # nebudeme zobrazovat nasledujici sloupce
    if col in ["OsaX", "OsaY","Mnoz_v_Porušení"]:
        continue
    print("#"*50) # oddelovac
    print(col, ": ", df[col].unique())

df.to_csv("ciste_opl.csv", index = False)