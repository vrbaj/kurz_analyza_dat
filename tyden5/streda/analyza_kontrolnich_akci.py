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

# spojeni dat zjisteni a rozkazu
data = zjisteni.merge(narizene_kc, how="left", on="CisloRozkazu")
print("#"*190)
print("Spojeni dat zjisteni a rozkazu")
print(tabulate(data.head()))

# spojeni k jednotlivym kontrolnim akcim doporucene KC a prisluslne rozkazy
data_doporuceni = ka_dle_rozkazu.merge(kc_dle_ka, how="left", on="CisloKA")
data_doporuceni["DoporuceneKC"] = data_doporuceni["DoporuceneKC"].apply(
    lambda x: set() if pd.isnull(x) else x
)
print("#"*190)
print("spojeni KA a KC a příslušné rozkzazy")
print(tabulate(data_doporuceni.head(),headers="keys", tablefmt="psql"))

# data_doporuceni obsahuji duplicity (protoze jeden rozkaz muze mit vice KA), timto to dokazeme
print("#"*190)
print("pocty vyskytu kazdeho rozkazu")
pocty = (data_doporuceni.groupby("CisloRozkazu")
                        .size()
                        .reset_index(name="pocet")
                        .sort_values("pocet", ascending=False)
                        .head(10)
)
print(tabulate(pocty, headers="keys", tablefmt="psql"))

#agregace KC pomocí sjednocení
data_doporuceni = data_doporuceni.groupby("CisloRozkazu")["DoporuceneKC"].agg(
    lambda x: set().union(*x)
).reset_index()
print("#"*190)
print("Doporucene KC pro rozkazy bez duplicit")
print(tabulate(data_doporuceni.head(), headers="keys", tablefmt="psql"))

# spojit vše
data_finalni = data.merge(data_doporuceni, on="CisloRozkazu", how="left")
data_finalni["DoporuceneKC"] = data_finalni["DoporuceneKC"].apply(
    lambda x: set() if pd.isnull(x) else x
)
print("#"*190)
print("Celkový přehled pozitivní/neg. KC a s nariznymi/doporucenymi KC")
print(tabulate(data_finalni.head(), headers="keys", tablefmt="psql"))

# ulozit
#data_finalni.to_excel("analyza.xlsx", index=False)

###########################
# Analyza dat
###########################
data_finalni["JeDoporuceni"] = data_finalni["DoporuceneKC"].apply(len)>0

data_finalni["PodilPozitivnich"] = (
    data_finalni["PocetPozitivnichKC"]/(
    data_finalni["PocetPozitivnichKC"] + data_finalni["PocetNegativnichKC"]
)
)

data_finalni["UspesnostNarizenychKC"] = (
    data_finalni.apply(
        lambda radek: len(radek["PozitivniKC"].intersection(radek["NarizeneKC"]))/len(radek["NarizeneKC"]),
        axis=1
    )
)

data_finalni["ShodaNarizenychDoporucenychKC"] = (
    data_finalni.apply(
        lambda radek: len(radek["NarizeneKC"].intersection(radek["DoporuceneKC"]))/
                      len(data_finalni["DoporuceneKC"]),
        axis=1
    )
)

print("#"*190)
print("Vysledky")
print(tabulate(
    data_finalni[data_finalni["JeDoporuceni"]].sort_values("ShodaNarizenychDoporucenychKC").head(20),
    headers="keys", tablefmt="psql"))

# data_finalni.to_excel("analyzovana_data.xlsx", index=False)

### Vizualizace
plt.figure()
sns.histplot(
    data_finalni[(data_finalni["PodilPozitivnich"]>0) & (data_finalni["PodilPozitivnich"]<1)]
    , x="PodilPozitivnich", hue="JeDoporuceni",
    element="step", stat="density", common_norm=False
)
plt.show()