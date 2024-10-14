# Importy
import pandas as pd
from sqlalchemy import create_engine, MetaData

# Vytvoreni konektoru na databzi
engine = create_engine("sqlite:///databaze.db", echo=True)
# Ziskani metadat k databazi a vraceni nazvu tabulek v databazi
metadata = MetaData()
metadata.reflect(bind=engine)
nazvy_tabulek = metadata.tables.keys()
print("\n---------SEZNAM TABULEK---------")
print(list(nazvy_tabulek))

# Import tabulky z SQL databaze
query_partneri = "SELECT * FROM partneri"
df_partneri = pd.read_sql(query_partneri, engine)
print("\n---------TABULKA PARTNERU---------")
print(df_partneri)

query_transakce = "SELECT * FROM transakce"
df_transakce = pd.read_sql(query_transakce, engine)
print("\n---------TABULKA TRANSAKCE---------")
print(df_transakce)

# Ukazka vyberu sloupce v tabulce
print("\n---------VYBER SLOUPCU---------")
# SELECT ico, nazev, kontakt_prijmeni
# FROM partneri
print(df_partneri[["ico", "nazev", "kontakt_prijmeni"]])
# Pomoci lokatoru
# print(df_partneri.loc[:, ["ico", "nazev", "kontakt_prijmeni"]])

# Vyber prvnich radku tabulky
print("\n---------VYBER PRVNICH 10 RADKU TABULKY PARTNERU---------")
# SELECT * FROM partneri
# LIMIT 10
print(df_partneri.head(10))

# Vyber poslednich radku tabulky
print("\n---------VRACENI POSLEDNICH 10 RADKU TABULKY PARTNERU---------")
# Neco na styl
# SELECT * FROM partneri
# ORDER BY ico DESC
# LIMIT 10
print(df_partneri.tail(10))

# Ukazka prirazeni hodnoty noveho sloupce podle vzorce
print("\n---------PRIRAZENI NOVEHO SLOUPCE TABULCE TRANSAKCE---------")
# SELECT *, castka/1000 AS castka_tis
# FROM transakce

# Vytvori se nova kopie tabulky s novym sloupcem
print(df_transakce.assign(castka_tis=df_transakce["castka"] / 1000))

# Prirazeni noveho sloupce puvodni tabulce
print(df_transakce.columns)
df_transakce["castka_tis"] = df_transakce["castka"] / 1000
# Vraceni vsech sloupcu tabulky pro ukazani noveho sloupce
print(df_transakce.columns)

# Filtrovani radku podle hodnoty ve sloupci
print("\n--------FILTR TRANSAKCI PODLE MENY--------")
# SELECT * FROM transakce
# WHERE mena = 'CZK'
print(df_transakce[df_transakce["mena"] == "CZK"])

# Kombinace filtru
print("\n--------FILTR TRANSAKCI PODLE CZK MENY A NAD 10000--------")
# SELECT * FROM transakce
# WHERE mena = 'CZK' AND castka > 10000
print(df_transakce[(df_transakce["mena"] == "CZK") & (df_transakce["castka"] > 10000)])

print("\n--------FILTR PRO VSECHNY EUR TRANSAKCE NEBO TRANSAKCE NAD 50000 CZK--------")
# SELECT * FROM transakce
# WHERE mena = 'EUR' OR castka > 50000
print(df_transakce[(df_transakce["mena"] == "EUR") |
                   ((df_transakce["castka"] > 50_000) & (df_transakce["mena"] == "CZK"))])

# Nalezeni radku s NULL hodnotami
print("\n--------NALEZENI RADKU S NULL HODNOTAMI VE SLOUPCI DATUM")
# SELECT * FROM transakce
# WHERE datum IS NULL
print(df_transakce[df_transakce["datum"].isna()])

# Alternativne, soucet vsech NULL radku pro sloupce
print(df_transakce.isna().sum())

# Hledam vsechny transakce pro ico 29776767 a 05902133
print("\n-------VRACENI VSECH TRANSAKCI PRO ZVOLENA ICO-------")
print(df_transakce[df_transakce["ico"].isin(["76767", "05902133"])])
print("\n-------VRACENI VSECH TRANSAKCI PRO CAST ICO-------")
print(df_transakce[df_transakce["ico"].str.contains("67") |
                   df_transakce["ico"].str.contains("133")])

# Ukazka shlukovani pomoci GROUP BY
print("\n-------POCTY TRANSAKCI PODLE JEDNOTLIVYCH MEN-------")
# SELECT mena, COUNT(mena)
# FROM transakce
# GROUP BY mena
print(df_transakce.groupby("mena").size())

print("\n-------CELKOVA SUMA A PRUMERNA VYSE TRANSAKCI PODLE MEN-------")
# SELECT mena, SUM(castka), AVG(castka)
# FROM transakce
# GROUP BY mena
print(df_transakce.groupby("mena").agg({"castka": ["sum", "mean"]}))

# Shlukovani pomoci vice sloupcu
print("\n-------SUMA TRANSAKCI PODLE ICO A MEN-------")
# SELECT ico, mena, SUM(castka)
# FROM transakce
# GROUP BY ico, mena
print(df_transakce.groupby(["ico", "mena"])["castka"].sum())

# Slucovani tabulek podle klice
print("\n-------SLOUCENI OBOU TABULEK PODLE ICO-------")
# SELECT * FROM partneri
# LEFT JOIN transakce
# ON partneri.ico = transakce.ico
print(df_partneri.merge(df_transakce, left_on="ico", right_on="ico", how="left"))
# print(df_partneri.merge(df_partneri, on="ico", how="left").columns)

# Slucovani pomoci indexu
transakce_alt = df_transakce.set_index("ico")
print("\n-------SLOUCENI TABULKY PRES INDEX-------")
print(df_partneri.merge(transakce_alt, left_on="ico", right_index=True, how="left"))

# Slouceni pomoci UNION
# SELECT * FROM partneri
# UNION
# SELECT * FROM partneri
print("\n-------SLOUCENI POMOCI UNION-------")
print(pd.concat([df_partneri, df_partneri]))# odstraneni duplicit .drop_duplicates(keep="first")

# Razeni radku tabulky
print("\n-------RAZENI RADKU TABULKY-------")
# SELECT * FROM transakce
# ORDER BY datum DESC
print(df_transakce.sort_values("datum", ascending=False))

# Modifikace hodnot v tabulce
print("\n-------ZMENA MENY NA HUF PRO TRANSAKCE U ICO 29776767-------")
# UPDATE transakce
# SET mena = 'HUF'
# WHERE ico = '29776767'

df_transakce.loc[df_transakce["ico"] == "29776767", "mena"] = "HUF"
print(df_transakce.loc[df_transakce["ico"] == "29776767", "mena"])

# Mazani casti tabulky
print("\n-------SMAZANI TRANSAKCI PRO ICO '74521056'-------")
# DELETE FROM transakce
# WHERE ico = '74521056'
df_transkace = df_transakce[df_transakce["ico"] != "74521056"]

# Smazani celeho sloupce castka_tis primo v tabulce
df_transakce.drop("castka_tis", axis=1, inplace=True)
print(df_transakce.columns)

# Smazani vsech radku s NULL hodnotami primo v tabulce
print(df_transakce.shape)
df_transakce.dropna(axis=0, inplace=True)
print(df_transakce.shape)

#TODO: Vsechny korunove transakce v cervnu 2023
#TODO: Soucty EUR transakci pro jednotlive firmy (udaj firmy bude jeji nazev misto ICO)