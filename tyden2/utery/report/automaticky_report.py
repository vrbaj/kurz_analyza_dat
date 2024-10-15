from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, Image, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm

# Nastaveni fontu pro dokument
pdfmetrics.registerFont(TTFont("Arial", "font/arial.ttf"))
pdfmetrics.registerFont(TTFont("Courrier", "font/courbd.ttf"))

import pandas as pd

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
celkova_vybrana_castka = data_kontroly["penalty"].sum()
