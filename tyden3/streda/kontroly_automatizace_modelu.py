# Importy
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, balanced_accuracy_score

# Načtení dat
data = pd.read_pickle("../utery/kontroly_ocistene.pkl")
# Zapomenutá oprava druhu vozidla
data["Druh_vozidla"] = data["Druh_vozidla"].fillna("nezjištěno")

# Zákódování porušení
data["Poruseni"] = data["Poruseni"].map({"ANO": 1, "NE": 0})

# Definice parametrů jednotlivých modelů pro grid search
parametry = {
    "Logistická regrese": {"C": [0.001, 0.01, 0.1, 1, 10, 100, 1000]},
    "Rozhodovací strom": {"max_depth": [5, 10, 20, None],
                          "min_samples_split": [2, 5, 10, 20],
                          "max_features": ["sqrt", "log2", None]},
    # "Náhodný les": {"max_depth": [5, 10, 20, None],
    #                 "min_samples_split": [2, 5, 10, 20],
    #                 "max_features": ["sqrt", "log2", None],
    #                 "n_estimators": [5, 11, 21],
    #                 "max_samples": [0.4, 0.6, 0.8, 1]
    #                     },
}
# Vypsání klíčů slovníku
# print(parametry.keys())
# Vypsání parametrů konkrétního modelu
# print(parametry["Náhodný les"])

# Inicializace modelů
modely = {
    "Logistická regrese": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Rozhodovací strom": DecisionTreeClassifier(class_weight="balanced"),
    # "Náhodný les": RandomForestClassifier(class_weight="balanced")
}

# Uložení nejlepších parametrů
nejlepsi_parametry = []

# Iterace skrz jednotlivé útvary
utvary = data["Utvar"].unique()

# Sloupce mazané při tvorbě příznaků (jelikož nejsou číselné)
mazane_sloupce = ["Celni_Urad", "Poruseni", "Kontrolni_Cinnost",
                  "Misto_kontoly", "Druh_vozidla", "Stat", "Pohlavi_porusitele",
                  "Utvar"]

# Sloupce zakódované pomocí frekvenčního kódování
kategoricke_sloupce = ["Celni_Urad", "Misto_kontoly", "Druh_vozidla", "Stat"]

for utvar in utvary:
    # Iterace skrz kontrolní činnosti
    # Unikátní hodnoty kontrolní činnosti pro data daného útvaru
    cinnosti = data[data["Utvar"] == utvar]["Kontrolni_Cinnost"].unique()

    for cinnost in cinnosti:
        print(f"===== {utvar} - {cinnost} =====")
        # Počet porušení a počet kontrol bez porušení
        subset = data[(data["Utvar"] == utvar) &
                      (data["Kontrolni_Cinnost"] == cinnost)]
        # metoda get vrací hodnotu pro daný index, nebo
        # hodnotu uvededenou v druhém argumentu, pokud index chybí
        pocet_poruseni = subset["Poruseni"].value_counts().get(1, 0)
        pocet_ok = subset["Poruseni"].value_counts().get(0, 0)
        # Porovnání počtu porušení a počtu kontrol bez porušení a eliminace subsetů
        # s nízkým počtem dat
        if (pocet_poruseni < 100) or (pocet_ok < 100):
            print(f"Přeskakuji {utvar} - {cinnost} (nedostatek dat)")
            continue

        # Předzpracování dat
        # Tabulka s příznaky
        priznaky = subset.drop(columns=mazane_sloupce)

        # One-hot encoding pro pohlaví
        kodovane_pohlavi = pd.get_dummies(subset[["Pohlavi_porusitele"]]).astype(int)
        priznaky = pd.concat([priznaky, kodovane_pohlavi], axis=1)

        # Frekvenční kódování
        for sloupec in kategoricke_sloupce:
            # Spočtení relativních četností pro hodnoty ve sloupci
            frekvence = subset[sloupec].value_counts(normalize=True).to_dict()
            # Namapování četností podle hodnoty ve sloupci
            priznaky[sloupec] = subset[sloupec].map(frekvence)

        # Definice výstupu
        vystup = subset["Poruseni"]

        # Rozdělení dat na trénovací a testovací
        X_train, X_test, y_train, y_test = train_test_split(priznaky, vystup,
                                                            test_size=0.2)
        # Iterace přes zvolené modely
        for nazev, model in modely.items():
            # Nastavení grid search pro parametry daného modelu
            grid_search = GridSearchCV(model, parametry[nazev], cv=5,
                                       scoring="balanced_accuracy", n_jobs=-1)
            # Natrénování všech modelů
            grid_search.fit(X_train, y_train)
            # Nalezení nejlepšího modelu
            nejlepsi_model = grid_search.best_estimator_

            # Vyhodnocení klasifikace na neznámých datech
            y_pred = nejlepsi_model.predict(X_test)
            uar = balanced_accuracy_score(y_test, y_pred)
            print(f"{nazev} - Report výsledků:\n{classification_report(y_test, y_pred)}")
            print(f"UAR: {uar:.2%}")

            # Uložení výsledků
            nejlepsi_parametry.append({
                "Utvar": utvar,
                "Kontrolni_Cinnost": cinnost,
                "Model": nazev,
                "Nejlepší parametry": grid_search.best_params_,
                "UAR": uar
            })

# Uložení nejlepších parametrů pro každý útvar, kontrolní činnost a model do tabulky
parametry_df = pd.DataFrame(nejlepsi_parametry)

# Uložení tabulky do CSV
parametry_df.to_csv("nejlepsi_parametry.csv", index=False)