import pandas
import geopandas
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib

df = pandas.read_excel("OPL_VSCHT.xlsx", decimal=",")
print(df.columns)

for col in df.columns:
    if col in ["Cas_Zjisteni","OsaX", "OsaY","OsaX_txt","OsaY_txt"]:
        continue
    print("#"*50)
    print(col, ": ", df[col].unique())

df = df.drop(columns=["Kraj_zjisteni_poruseni","Okres_zjisteni_poruseni",
                      "Bydliste_Porusitele","Narodnost_Porusitele","Typ_Vozidla",
                      "Rozkaz_ID","Popis_Mista_Zjisteni","CisloTydne",
                      "Km","Mesto","Kontrolni_Cinnost", "Duplicita","Utvar"])