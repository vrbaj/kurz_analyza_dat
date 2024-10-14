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
print(df_transakce[df_transakce["ico"].str.contains("67") | df_transakce["ico"].str.contains("133")])
