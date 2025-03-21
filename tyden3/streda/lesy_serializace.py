# Importy
import pandas as pd
from tabulate import tabulate
from matplotlib import pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, balanced_accuracy_score
import joblib
import unicodedata

def odstraneni_diakritiky(text):
    normalizace = unicodedata.normalize("NFKD", text)
    ascii_text = normalizace.encode("ASCII", "ignore")
    return ascii_text.decode("ASCII")

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

# Odfiltrování vybraných celních úřadů (Liberec, Moravskoslezský kraj)
# print(data.shape)
# data = data[(data["Celni_Urad"] != "CÚ pro Liberecký kraj") &
#             (data["Celni_Urad"] != "CÚ pro Moravskoslezský kraj")]
# print(data.shape)

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

# Inicializace modelu náhodného lesa
model = RandomForestClassifier(random_state=42, class_weight="balanced")
parametry = {"max_depth": [5, 10],
             "min_samples_split": [2, 5],
             "max_features": ["sqrt"],
             "n_estimators": [51],
             "max_samples": [0.8]
             }

# Trénování modelu a vyhodnocení přesnosti klasifikace
# Filtrace příznaků a výstupu podle konkrétní kontrolní činností
kontrolni_cinnosti = data["Kontrolni_Cinnost"].unique()

# Iterace skrz jednotlivé kontrolní činnosti
tabulka_vysledku = pd.DataFrame(columns=["Cinnost", "Nastaveni_modelu",
                                         "UAR", "Soubor_s_modelem"])
for cinnost in kontrolni_cinnosti:
    # Filtrace podle dané činnosti
    priznaky_kc = priznaky[data["Kontrolni_Cinnost"] == cinnost]
    vystup_kc = vystup[data["Kontrolni_Cinnost"] == cinnost]

    # Zjištění počtu vzorků úspěšných a neúspěšných kontrol pro danou činnost
    # Pro příliš malé počty nebude model fungovat dobře
    # Metoda get vrátí hodnotu pod zadaným indexem, pokud nenajde index, vrátí
    # hodnotu uvedenou jako druhý argument
    pocet_poruseni = vystup_kc.value_counts().get(1, 0)
    pocet_ok = vystup_kc.value_counts().get(0, 0)

    # Podmínka pro přeskočení tréningu
    if (pocet_poruseni < 100) or (pocet_ok < 100):
        print(f"{cinnost} neobsahuje dostatek dat, přeskakuji...")
        continue # přeruší běh současné iterace a pokračuje další činností
    else:
        print(f"{cinnost} obsahuje dostatek dat, trénuji model.")

    # Rozdělení dat na trénovací a testovací
    X_train, X_test, y_train, y_test = train_test_split(priznaky_kc, vystup_kc,
                                                        test_size=0.2, random_state=42)

    # Trénování a nalezení nejlepšího nastavení modelu
    # n_jobs=-1 pro využití všech vláken procesoru
    grid_search = GridSearchCV(model, parametry, cv=5, scoring="balanced_accuracy",
                               n_jobs=-1, verbose=10)
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
    nazev_modelu = odstraneni_diakritiky(cinnost).replace(" ", "_")
    novy_radek = pd.DataFrame([[cinnost, grid_search.best_params_,
                                uar, nazev_modelu]], columns=tabulka_vysledku.columns)
    tabulka_vysledku = pd.concat([novy_radek, tabulka_vysledku], ignore_index=True)
    k_ulozeni = {"model": nejlepsi_model,
                 "data_x": X_test,
                 "data_y": y_test,
                 "features": priznaky_kc.columns}
    joblib.dump(k_ulozeni, f"modely/{nazev_modelu}.joblib")
    # Feature importance - spočtení permutation importance jednotlivých příznaků
    feature_importance = pd.Series(nejlepsi_model.feature_importances_,
                                   index=priznaky_kc.columns)
    feature_importance = feature_importance.sort_values(ascending=True)

    # Vykreslení feature importance
    fig, ax = plt.subplots(figsize=(10, 6))
    feature_importance.plot(kind="barh", ax=ax)
    ax.set_title(f"Feature importance náhodného lesa pro {cinnost}")
    ax.set_xlabel("Hodnota koeficientu")
    ax.set_ylabel("Příznak")
    plt.tight_layout()
    fig.savefig(f"nahodny_les/feature_importance_{cinnost}.png")

tabulka_vysledku.sort_values(by="Soubor_s_modelem", ascending=False, inplace=True)
tabulka_vysledku.to_csv("tabulka_vysledku.csv", index=False)