# Importy
import pandas as pd
from tabulate import tabulate
from matplotlib import pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, balanced_accuracy_score


# Nastavení seedu pro sjednocené generování náhodných hodnot
np.random.seed(42)
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
# Iterace skrz kategorické sloupce
for sloupec in kodovane_sloupce:
    # Vytvoření relativních četností pro jednotlivé sloupce a uložení do slovníku
    frekvencni_kodovani = data[sloupec].value_counts(normalize=True).to_dict()
    # Namapování četností na jednotlivé hodnoty v daném sloupci a uložení jako
    # nového sloucpce do tabulky s příznaky
    priznaky[sloupec] = data[sloupec].map(frekvencni_kodovani)

# Definice výstupu
vystup = data["Poruseni"]

# Inicializace modelu logistické regrese
model = LogisticRegression(max_iter=1000, class_weight="balanced")
parametry = {"C": [0.001, 0.01, 0.1, 1, 10, 100, 1000]}

# Trénování modelu a vyhodnocení přesnosti klasifikace
# Filtrace příznaků a výstupu podle konkrétní kontrolní činností
cinnost = 'VV - tabák a tabákové výrobky'

# Filtrace příznaků podle zvolené činnosti
priznaky_kc = priznaky[data["Kontrolni_Cinnost"] == cinnost]
vystup_kc = vystup[data["Kontrolni_Cinnost"] == cinnost]

# Rozdělení dat na trénovací a testovací
X_train, X_test, y_train, y_test = train_test_split(priznaky_kc, vystup_kc,
                                                    test_size=0.2, random_state=42)

# Trénování a nalezení nejlepšího nastavení modelu
grid_search = GridSearchCV(model, parametry, cv=5, scoring="balanced_accuracy")
grid_search.fit(X_train, y_train)
nejlepsi_model = grid_search.best_estimator_

# Vyhodnocení přesnosti klasifikace na testovacích datech
# Predikce na neznámých datech
y_pred = nejlepsi_model.predict(X_test)
# Unweighted Average Recall
uar = balanced_accuracy_score(y_test, y_pred)
# Vypsání výsledků klasifikace
print(f"{cinnost} - Nejlepši nastavení: {grid_search.best_params_}")
print(f"Report výsledků:\n{classification_report(y_test, y_pred)}")
print(f"Výsledek UAR: {uar:.2%}")

# Feature importance - zobrazení vah jednotlivých příznaků
feature_importance = pd.Series(nejlepsi_model.coef_[0], index=priznaky_kc.columns)
feature_importance = feature_importance.sort_values(ascending=True)

# Graf s feature importance
fig, ax = plt.subplots(figsize=(10, 6))
feature_importance.plot(kind="barh", ax=ax)
ax.set_title(f"Feature importance logistické regrese pro {cinnost}")
ax.set_xlabel("Hodnota koeficientu")
ax.set_ylabel("Příznak")
plt.tight_layout()
plt.show()