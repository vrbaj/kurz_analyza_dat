# Import knihoven
import pyodbc
import pandas as pd
from tabulate import tabulate
from pathlib import Path
from matplotlib import pyplot as plt

# Stazeni dat (pokud jiz nejsou ulozena v adresari jako CSV soubor)
def stahni_data():
    # Cesta k souboru s ulozenymi daty
    cesta_data = Path("kontroly_s_mistem_a_prostredkem.csv")

    # Pokud soubor neexistuje, stahnou se data z databaze a ulozi jako CSV
    # soubor
    if not cesta_data.exists():
        # Konektor na databazi
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=10.2.35.17;"
            "DATABASE=MD2_VSCHT;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        # Nacteni vlastni query
        query_cesta = Path("sql_query", "kontroly_s_mistem_a_prostredkem.sql")
        query = query_cesta.read_text()
        data_vse = pd.read_sql(query, conn)

        # Ulozeni souboru
        data_vse.to_csv(cesta_data, index=False, encoding="utf-8", sep=";")

    # Data jiz jsou stazena
    else:
        # Nacteni dat primo ze souboru
        data_vse = pd.read_csv(cesta_data, sep=";")

    # Vratit nactena data jako vystup z funkce
    return data_vse

# Stazeni dat
data = stahni_data()

print("Ukazka zpracovavanych dat")
print(tabulate(data.head(20), headers="keys", tablefmt="psql"))

# Pocty prazdnych bunek v kazdem sloupci
prazdne = data.isnull().sum().reset_index(name="pocet")
print("#" * 150)
print("Prazdne bunky ve sloupcich")
print(tabulate(prazdne, headers="keys", tablefmt="psql"))

# Typy mist, kde neni vyplnen typ mista
mista_bez_transportu = data[data["CisloTransportu"].isnull()]
mista_bez_transportu = (mista_bez_transportu.groupby(["CisloMista", "TypMista"]).size()
                            .sort_values(ascending=False).reset_index(name="pocet"))
print("#" * 150)
print("Mista, kde neni vyplnen transport")
# print(mista_bez_transportu.shape)
print(tabulate(mista_bez_transportu, headers="keys", tablefmt="psql"))

# Vyplneni typu transportu v prazdnych bunkach
data["TypTransportu"] = data["TypTransportu"].fillna("nevyplněno")
data["CisloTransportu"] = data["CisloTransportu"].fillna(-1)

# Kontrola duplicit
print("#" * 150)
print("Celkova velikost:", data.shape, "Bez duplicit", data.drop_duplicates().shape)

# Odstraneni duplicitnich radku
data.drop_duplicates(inplace=True)

# Unikatni typy transportu a jejich cetnosti
unikatni_transporty = data["TypTransportu"].value_counts().reset_index(name="pocet")
print("#" * 150)
print("Unikatni typy transportu a jejich cetnosti")
print(tabulate(unikatni_transporty, headers="keys", tablefmt="psql"))

# Unikatni typy mist a jejich cetnosti
unikatni_mista = data["TypMista"].value_counts().reset_index(name="pocet")
print("#" * 150)
print("Unikatni typy mist a jejich cetnosti")
print(tabulate(unikatni_mista, headers="keys", tablefmt="psql"))

# Nastaveni datoveho typu jednotlivym identifikatorum
cols = ["CisloKontroly", "CisloRozkazu", "CisloMista", "CisloTransportu"]
data[cols] = data[cols].astype("Int64", errors="raise")

# Pocty vykazanych kontrol podle typu mista a typu transportu
kombinace = (
    data.groupby(["TypMista", "TypTransportu"])
        .size() # cetnosti
        .reset_index(name="Pocet") # prevedeni na tabulku
        .sort_values(["TypMista", "Pocet"], ascending=[True, False])
)
print("#" * 150)
print("Cetnosti pro kombinace misto - transport")
print(tabulate(kombinace.head(20), headers="keys", tablefmt="psql"))