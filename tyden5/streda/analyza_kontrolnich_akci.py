import pyodbc
import pandas as pd
from tabulate import tabulate
from pathlib import Path
from matplotlib import pyplot as plt
import seaborn as sns
from connection_string import conn_string

# fuknci pro stahovani dat
def stahni_data(nazev_query):
    # podivat se zda nemame data stazene
    cesta_data = Path(nazev_query).with_suffix(".csv")

    # pokud je mame tak pouzijeme
    if cesta_data.exists():
        data = pd.read_csv(cesta_data)

    # pokud ne tak stahneme
    else:
        conn = pyodbc.connect(conn_string)
        # nacteni SQL dotazu
        query_cesta = Path("sql_query", nazev_query + ".sql")
        query = query_cesta.read_text(encoding="utf-8")

        # stahovani dat
        data = pd.read_sql(query, conn)
        # ulozeni pro dalsi pouziti
        data.to_csv(cesta_data, index=False, encoding="utf-8")
    return data

# nejprve zavolame poprve cimz se stahnou data
zjisteni = stahni_data("pocty_kc_dle_zjisteni")
#print(tabulate(zjisteni.head(), headers="keys", tablefmt="psql"))

# převedeme NehgativniKC i PozitivniKC na mnozinu -> tim nejen usnadnime dalsi zpracovani dat ale i deduplikujeme zaznamy
zjisteni["NegativniKC"] = zjisteni["NegativniKC"].apply(
    lambda x: set() if pd.isnull(x) else
    set(sorted(x.strip().split(",")))
)
zjisteni["PozitivniKC"] = zjisteni["PozitivniKC"].apply(
    lambda x: set() if pd.isnull(x) else
    set(sorted(x.strip().split(",")))
)
print("#"*190)
print("Pozitivni a negativni zjisteni pro jednotlive rozkazy")
print(tabulate(zjisteni.head(), headers="keys", tablefmt="psql"))


# Stazeni dat pro jednotlive rozkazy
narizene_kc = stahni_data("narizene_kc_dle_rozkazu")
narizene_kc["NarizeneKC"] = narizene_kc["NarizeneKC"].apply(
    lambda x: set() if pd.isnull(x) else
    set(sorted(x.strip().split(",")))
)

print("#"*190)
print("Narizene KC pro jednotlive rozkazy")
print(tabulate(narizene_kc.head(), headers="keys", tablefmt="psql"))

# prehled rozkazu a z jakych kontrolnich akci vychazeji
ka_dle_rozkazu = stahni_data("KA_dle_rozkazu")
print("#"*190)
print("Prehled KC konztolnich akci dle rozkazu")
print(tabulate(ka_dle_rozkazu.head(), headers="keys", tablefmt="psql"))

# prehled doporucenych KC pro jednotlive k akce
kc_dle_ka = stahni_data("doporucene_KC_dle_KA")
kc_dle_ka["DoporuceneKC"] = kc_dle_ka["DoporuceneKC"].apply(
    lambda x: set() if pd.isnull(x) else
    set(sorted(x.strip().split(",")))
)
print("#"*190)
print("Prehled doporucenych KC pro jednotlive KA")
print(tabulate(kc_dle_ka.head(),headers="keys", tablefmt="psql"))
