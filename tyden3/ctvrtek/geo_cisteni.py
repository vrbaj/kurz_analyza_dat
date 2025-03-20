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
    if col in ["Cas_Zjisteni","OsaX", "OsaY","OsaX_txt","OsaY_txt"]:
        continue
    print("#"*50)
    print(col, ": ", df[col].unique())

#Rok_narozeni_porusitele
df_pracovni = df[df["Rok_narozeni_porusitele"]>1900]
df_pracovni["Rok_narozeni_porusitele"] = \
    df_pracovni["Rok_narozeni_porusitele"].apply(
        lambda x: 1999 if x == 2099 else x)
sns.histplot(df_pracovni, x="Rok_narozeni_porusitele")
plt.show()