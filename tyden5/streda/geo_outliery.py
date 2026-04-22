"""
Analýza outlierů v kontextu lokace provedených kontrol.
Body reprezentující hranici je potřeba stáhnout zde:
https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/

"""
import contextily as ctx
import folium
import geopandas
from shapely.geometry import Point
import pyodbc
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

FILTRACE = False
DB = False

# cesta k soubouru s hranicí jako řetězec znaků string
cesta_hranice = str(Path("./ne_10m_admin_0_countries.zip").resolve())
# kontrola cesty k souboru s hranicemi
print(cesta_hranice)

# načtení bodů hranic
svet_hranice = geopandas.read_file(cesta_hranice)
# Česko hranice (pozor, soubor obsahuje hranice všech států)
cesko_hranice = svet_hranice[svet_hranice["NAME_EN"] == "Czech Republic"]

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
        SELECT d.axisx, d.axisy, a.AuditAction, d.isCrimact,
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
    zahranicni_kontroly_filtrovane.to_file("kontroly_filtrovane.shp")
else:
    zahranicni_kontroly_filtrovane = geopandas.read_file("kontroly_filtrovane.shp")
    print(zahranicni_kontroly_filtrovane)

    print("================== Příprava interaktivní mapy =======================")
    interaktivni_mapa = folium.Map(location=[50.08, 14.42], zoom_start=6)
    print(zahranicni_kontroly_filtrovane.columns)
    for idx, radek in zahranicni_kontroly_filtrovane.iterrows():
        kontrolni_cinnost = radek["AuditActio"]
        vysledek_kontrolni_cinnost = radek["isCrimact"]
        # crecord = radek["crecord"]
        if vysledek_kontrolni_cinnost == 0:
            barva = "blue"
        else:
            barva = "red"
        folium.CircleMarker(
            location=[radek["axisy"], radek["axisx"]],
            radius = 3,
            fill=True,
            color=barva,  # barva podle výsledku kontroly
            fill_opacity=0.7,
            # popisek bodu se souřadnicemi a kontrolní činností
            popup=f"X={radek["axisx"]}, Y={radek["axisy"]} - kontrolni činnost: {kontrolni_cinnost},"
                  #f"kontrola = {crecord}",
        ).add_to(interaktivni_mapa)
    # vykreslení hranice (pozor, pro větší přesnost je potřeba mít hranici s vícero body, což povede
    # na výpočetně náročnější program
    folium.GeoJson(data=cesko_hranice.boundary.__geo_interface__,
                   style_function=lambda feature: {"color": "blue", "weight": 3},).add_to(interaktivni_mapa)
    # uložení map do html pro následnou práci
    interaktivni_mapa.save("interaktni_mapa.html")

    # odstaranění kontrol bez souřadnic
    zahranicni_kontroly_filtrovane = zahranicni_kontroly_filtrovane[(zahranicni_kontroly_filtrovane["axisx"] != 0)
                                                                    & (zahranicni_kontroly_filtrovane["axisy"] != 0)]
    print(f"Počet kontrol filtrovaných s validními souřadnicemi {zahranicni_kontroly_filtrovane.shape[0]}")
    # výsledky do statické mapy z openstreetmaps
    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    # specifikovat souřadnicový systém pro google maps, atp.
    zahranicni_kontroly_filtrovane_web = zahranicni_kontroly_filtrovane.to_crs(epsg=3857)
    # body kontrol do mapy
    zahranicni_kontroly_filtrovane_web.plot(ax=ax, marker="o", color="red", marker_size=50)
    # přidání podkladové mapy

