# Importy
import pandas as pd
from tabulate import tabulate
from matplotlib import pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, balanced_accuracy_score

# Načtení dat
# Dvě tečky pro přístup do složky o úroveň výše
data = pd.read_pickle("../utery/kontroly_ocistene.pkl")
data = data[['Celni_Urad', 'Poruseni', 'Kontrolni_Cinnost', 'Misto_kontoly',
       'Cas_Zjisteni', 'Druh_vozidla', 'Stat', 'Pohlavi_porusitele', 'Utvar',
       'datum_mesic', 'datum_den_tydne']]

# Problém s druhem vozidla - chybějící hodnoty
data["Druh_vozidla"] = data["Druh_vozidla"].fillna("nezjištěno")

# Volba mobilního dohledu
data = data[data["Utvar"] == "Mobilní dohled"]

# Zakódování sloupce Poruseni
data["Poruseni"] = data["Poruseni"].map({"ANO": 1, "NE": 0})

# Tabulka příznaků
mazane_sloupce = ["Poruseni", "Kontrolni_Cinnost", "Utvar",
                  "Pohlavi_porusitele", "Stat", "Celni_Urad",
                  "Misto_kontoly", "Druh_vozidla"]
priznaky = data.drop(columns=mazane_sloupce)

# one-hot encoding pro Pohlaví
kodovane_pohlavi = pd.get_dummies(data[["Pohlavi_porusitele"]]).astype(int)

# Sloučení tabulek příznaky a kódované pohlaví
priznaky = pd.concat([priznaky, kodovane_pohlavi], axis=1)

# Frekvenční kódování (frequency encoding) zbývajících sloupců
kodovane_sloupce = ["Celni_Urad", "Misto_kontoly", "Druh_vozidla", "Stat"]
