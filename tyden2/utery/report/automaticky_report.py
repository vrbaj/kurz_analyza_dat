from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, Image, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm

# Nastaveni fontu pro dokument
pdfmetrics.registerFont(TTFont("Arial", "font/arial.ttf"))
pdfmetrics.registerFont(TTFont("Courrier", "font/courbd.ttf"))

import pandas as pd
import numpy as np

# Nacteni dat
data_kontroly = pd.read_csv("Data_kontroly.csv", sep=";")
# Datum od a do
datum_od = data_kontroly["LocDate"].min()
datum_do = data_kontroly["LocDate"].max()
# Prevedeni na tvar DD.MM.RRRR
datum_od_seznam = datum_od.split(" ")[0].split("-") # Rozdeleni podle mezery a pak podle pomlcky
datum_od_seznam = datum_od_seznam[::-1] # Otoceni poradi prvku seznamu
datum_od_pro_tisk = ".".join(datum_od_seznam) # Slouceni seznamu do retezce pres tecku jako oddelovac

datum_do_seznam = datum_do.split(" ")[0].split("-")
datum_do_seznam = datum_do_seznam[::-1]
datum_do_pro_tisk = ".".join(datum_do_seznam)

# Pocet vybranych pokut a celkova vybrana castka
pocet_pokut = data_kontroly[data_kontroly["penalty"] > 0].shape[0]
celkova_vybrana_castka = f"{data_kontroly["penalty"].sum():,}".replace(",",'\xa0')

# Vytvoreni objektu pro dokument
dokument = SimpleDocTemplate("report.pdf", pagesize=A4)
max_sirka = dokument.width
max_vyska = dokument.height
print(max_sirka, max_vyska)
# Nacteni preddefinovanych stylu pro text a dokument
styly = getSampleStyleSheet()
# Vlastni nastaveni stylu pro text a tabulku
styl_nazev = ParagraphStyle(
    name="nazev", # nazev stylu
    fontSize=48, # velikost fontu
    alignment=1, # zarovnani na stred
    spaceBefore=0, # mezera pred odstavcem
    spaceAfter=0, # mezera za odstavcem
    leading=48, # radkovani, minimalne stejne jako velikost fontu
    fontName="Courrier" # nazev fontu, vyuzivame vlastni definovany font
)

styl_nadpis1 = ParagraphStyle(
    name="nadpis1",
    fontSize=24,
    spaceBefore=12,
    spaceAfter=8,
    leading=24,
    fontName="Courrier"
)

styl_nadpis2 = ParagraphStyle(
    name="nadpis2",
    fontSize=18,
    spaceBefore=12,
    spaceAfter=8,
    leading=18,
    fontName="Courrier"
)
# Styl pro normalni text z preddefinovaneho stylu
styl_normalni = styly["Normal"]
styl_normalni.name = "normalni"
styl_normalni.fontName = "Arial"

# Prvni stranka dokumentu - nazev
odsazeni_do_pul_stranky = Spacer(1, max_vyska / 2 - 48)
nazev_dokumentu = Paragraph("Automatizovaný report", styl_nazev)
zalomeni_stranky = PageBreak()

# Kratky uvod
nadpis_kratky_uvod = Paragraph("Krátký popis kontrol", styl_nadpis1)
text_k_popisu_kontrol = (f"V období od {datum_od_pro_tisk} do {datum_do_pro_tisk} bylo"
                         f" provedeno {pocet_pokut} kontrol. Celkově byly uloženy pokuty"
                         f"ve výši {celkova_vybrana_castka} Kč.")
odstavec_kratky_uvod = Paragraph(text_k_popisu_kontrol, styl_normalni)

# Tabulka
# Nahrani tabulky, jez bude vlozena
tabulka = pd.read_csv("mezirocni_zmeny_kontroly.csv")
# Zmena datoveho typu u mesice pro potlaceni zmeny na float
tabulka["mesic"] = tabulka["mesic"].astype(str)
# Prevedeni tabulky na seznam seznamu
tabulka_v_seznamech = [["MĚSÍC", "2022", "2023", "MEZIROČNÍ ZMĚNA"]] + \
                      np.array(tabulka).tolist()
nadpis_pro_tabulku = Paragraph("Tabulka meziročních změn v počtu kontrol",
                               styl_nadpis2)
tabulka_report = Table(tabulka_v_seznamech)
tabulka_report.setStyle(
    # 'Vlastnost', rozsah bunek definovany cislem sloupce a radku, hodnota
    [("FONTNAME", (0, 0), (-1, -1), "Arial"),
     ("BACKGROUND", (0, 0), (-1, 0), colors.grey), # pozadi hlavicky
     ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke), # text hlavicky
     ("ALIGN", (0, 0), (0, -1), "LEFT"), # zarovnani prvniho sloupce
     ("ALIGN", (-1, 0), (-1, -1), "RIGHT"), # zarovnani posledniho sloupce doprava
     ("BOTTOMPADDING", (0, 0), (-1, 0), 12), # odsazeni od spodni hrany bunky
     ("GRID", (0, 0), (-1, -1), 1, colors.black)] # ohraniceni bunek
)

# Vlozeni obrazku
nadpis_k_obrazku = Paragraph("Mapa výskytů kontrol", styl_nadpis2)
obrazek = Image("vyskyty_kontrol.png")
sirka, vyska = obrazek.wrap(0, 0)
obrazek.drawWidth = max_sirka
obrazek.drawHeight = max_sirka / sirka * vyska
# Ulozeni jednotlivych casti dokumentu
prvky_dokumentu = [
    odsazeni_do_pul_stranky,
    nazev_dokumentu,
    zalomeni_stranky,
    nadpis_kratky_uvod,
    odstavec_kratky_uvod,
    nadpis_pro_tabulku,
    tabulka_report,
    KeepTogether([nadpis_k_obrazku,obrazek]) # spolecne na stejne strance
]

# Vygenerovani dokumentu
dokument.build(prvky_dokumentu)