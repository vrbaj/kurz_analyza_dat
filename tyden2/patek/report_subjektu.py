from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT
import pandas as pd
pd.set_option("display.width", 10000)
pd.set_option("display.max_columnwidth", None)
pd.set_option("display.max_columns", None)
import json

'''Funkce pro uvodni stranu'''
def vytvor_uvodni_stranu(dokument):
    # Vlastni text nadpisu strany
    styl = dokument.styles.add_style("vlastni_styl", 1) # 1 znaci, ze se jedna o styl odstavce
    font = styl.font
    font.name = "Courier New"
    font.size = Pt(64)
    font.underline = True

    # Pridani odstavce s nazvem dokumentu
    odstavec = dokument.add_paragraph("PŘEHLED PODEZŘELÝCH SUBJEKTŮ", style="vlastni_styl")
    odstavec.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Pridani obrazku s logem
    # Novy prazdny odstavec
    odstavec = dokument.add_paragraph()
    odstavec.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    # Pridani obsahu do existujiciho odstavce
    obsah_odstavce = odstavec.add_run()
    obsah_odstavce.add_picture("logo.jpg", width=Cm(4.5))

# Vytvoreni objektu Document
dokument = Document()
# Vytvoreni titulni strany
vytvor_uvodni_stranu(dokument)
# Ulozeni dokumentu
dokument.save("report_podezrelych_subjektu.docx")