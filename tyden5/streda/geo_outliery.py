import geopandas
from shapely.geometry import Point
import pyodbc
import pandas as pd
from pathlib import Path

FILTRACE = True
DB = False

if FILTRACE:
    if DB:
        # definice připojení k DB
        CONN_STR = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=(localdb)\MSSQLLocalDB;"
            "DATABASE=MD2_VSCHT;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=no;"
        )
        # vytvoření připojení
        conn = pyodbc.connect(CONN_STR)
        # požadovaná SQL query
        query = """
        SELECT d.axisx, d.axisy, a.AuditAction, d.isCrimact
        FROM inetuser.MDx_Disorder d
        LEFT JOIN inetuser.MDx_AuditAction a ON d.cAuditAction = a.cAuditAction"""
        # načtení dat z db
        lokace = pd.read_sql(query, conn)
        # uložení do CSV
        lokace.to_csv("lokace.csv")
    else:
        # nahraní dat z CSV
        lokace = pd.read_csv("lokace.csv")

    # kontrola tabulky
    print(lokace.head())

    # převod souřadnic kontrol na geopandas body
    kontrola_souradnice = [Point(xy) for xy in zip(lokace["axisx"], lokace["axisy"])]
    # geopandas dataframe se souřadnicovým systémem výška/šířka ve stupních
    gdf = geopandas.GeoDataFrame(lokace, geometry=kontrola_souradnice, crs="EPSG:4326")
    print(gdf.head())

    # cesta k soubouru s hranicí jako řetězec znaků string
    cesta_hranice = str(Path("./ne_10m_admin_0_countries.zip").resolve())
    # kontrola cesty k souboru s hranicemi
    print(cesta_hranice)

    # načtení bodů hranic
    svet_hranice = geopandas.read_file(cesta_hranice)
    # Česko hranice (pozor, soubor obsahuje hranice všech států)
    cesko_hranice = svet_hranice[svet_hranice["NAME_EN"] == "Czech Republic"]
    # převod do Mercatorova válcového konformního zobrazení
    cesko_hranice_mercator = cesko_hranice.to_crs(epsg=32633)
    # výběr kontrol mimo ČR
    kontroly_zahranici = gdf[~gdf.within(cesko_hranice.geometry.iloc[0])]
    # zahraniční kontroly v MVK zobrazení
    kontroly_zahranici_mercator = kontroly_zahranici.to_crs(epsg=32633)
    # 5 km zóna, kvůli nepřesné hranici
    zona_5km = cesko_hranice_mercator.union_all().buffer(5000)
    # odfiltrujeme kontroly mimo pás 5000
    zahranicni_kontroly_filtrovane = kontroly_zahranici_mercator[~kontroly_zahranici_mercator.within(zona_5km)]
    # převod to GPS
    zahranicni_kontroly_filtrovane.to_crs(epsg=4326, inplace=True)
    # kontrola počtu kontrol mimo ČR a pásmo
    print(f"Počet kontrol mimo ČR: {zahranicni_kontroly_filtrovane.shape[0]}")
    # uložení kontrol do souboru
    zahranicni_kontroly_filtrovane.to_csv("kontroly_filtrovane.csv")
else:
    zahranicni_kontroly_filtrovane = geopandas.read_file("kontroly_filtrovane.csv")
    print(zahranicni_kontroly_filtrovane.head())