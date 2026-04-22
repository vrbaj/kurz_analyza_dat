import geopandas
from shapely.geometry import Point
import pyodbc
import pandas as pd
from pathlib import Path


DB = False

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