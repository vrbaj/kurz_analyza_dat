import pandas as pd
from sklearn.preprocessing import StandardScaler # Škálování dat na stejný interval
# Pipeline pro automatizaci předzpracování dat a trénování
from sklearn.pipeline import Pipeline
# Import funkce pro rozdělení na trénovací a testovací data, metriky pro křížovou validaci,
# objektu pro vyzkoušení různých nastavená hyperparametrů
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.svm import SVC # Support Vector Machine model
from sklearn.tree import DecisionTreeClassifier # Rozhodovací strom
from sklearn.ensemble import RandomForestClassifier # Náhodný les
from sklearn.metrics import accuracy_score, recall_score, precision_score, roc_curve, confusion_matrix
from matplotlib import pyplot as plt


# Nahrání dat
data = pd.read_csv("klasifikace_balancovany.csv")
# print(data.head())
print(data.info())
# Přejmenování prvního sloupce na "Vystup"
nazvy_sloupcu = data.columns.tolist() # Uložení názvy sloupců jako seznam
nazvy_sloupcu[0] = "Vystup" # Přejmenování prvního sloupce na "Vystup"
data.columns = nazvy_sloupcu #print Přiřazení změněného seznamu zpět tabulce

# Rozdělení dat do proměnné X (příznaky) a y (výstup) a transformace na matice a vektory
X = data.drop("Vystup", axis=1).to_numpy()
y = data["Vystup"].to_numpy()

# Rozdělení datasetu na trénovací a testovací sety
X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                    test_size=0.4, random_state=42)
# Až sem stačí provést jednou!
# Seznam objektů pro jednotlivé klasifikátory
seznam_clf = [SVC(), DecisionTreeClassifier(), RandomForestClassifier()]
seznam_nastaveni_parametru = [
    # Nastavení hyperparametrů pro SVM
    {"svm__C": [0.1, 1, 10], # Regularizační parametr
     "svm__kernel": ["linear", "rbf"], # Kernel (jádrová funkce)
     "svm__gamma": ["scale", "auto"]}, # Gamma parametr (pro 'rbf' kernel)
    # Nastavení hyperparametrů pro rozhodovací strom
    {"tree__max_depth": [3, 5, 10, None], # Maximální hloubka větvení
     "tree__min_samples_split": [2, 5, 10], # Minimální počet vzorků v uzlu před rozdělením
     "tree__min_samples_leaf": [1, 2, 4], # Minimální počet vzorků v koncovém uzlu
     "tree__criterion": ["gini", "entropy"]}, # Kriteriální funkce pro rozdělení vzorků v uzlu
    # Nastavení hyperparametrů pro náhodný les
    {"rf__n_estimators": [50, 100], # Počet modelů v náhodném lese
     "rf__max_depth": [3, 10, None], # Maximální hloubka větvení každého modelu
     "rf__min_samples_split": [2, 5], # Minimální počet vzorků v uzlu před rozdělením
     "rf__min_samples_leaf": [1, 2, 4], # Minimální počet vzorků v koncovém uzlu
     "rf__criterion": ["gini", "entropy"], # Kriteriální funkce pro rozdělení vzorků v uzlu
     "rf__bootstrap": [True, False]}, # Volba, zdali má být použit bootstrapping
]
# Vytvoření pipeline pro SVM klasifikaci
pipeline = Pipeline([
    ('scaler', StandardScaler()), # Škálování dat různých rozsahů na stejný interval
    ("svm", SVC()) # SVM klasifikátor
])

# Rozsah hyperparametrů
rozsah_parametru = {
    "svm__C": [0.1, 1, 10], # Parametr 'C' pro objekt 'svm' v pipeline
    "svm__kernel": ["linear", "rbf"], # Parametr 'kernel' pro objekt 'svm' v pipeline
    "svm__gamma": ["scale", "auto"] # Parametr 'gamma' pro objekt 'svm' v pipeline
}

# Grid search (zkoušení všech kombinací hyperparametrů
grid_search = GridSearchCV(pipeline, rozsah_parametru, cv=5, scoring='accuracy')
# Trénování dat pro všechny kombinace hyperparametrů
grid_search.fit(X_train, y_train)

# Vypsání nejlepších hyperparametrů pro SVM
print("-------------SVM-------------")
# grid_search.best_params_ vrací nastavení pro model s nejvyšší dosaženou přesností
# podle křížové validace
print(f"Nejlepší nastavení SVM: {grid_search.best_params_}.")
# Zjištění skóre z křížové validace trénovacích dat
cv_skore = cross_val_score(grid_search.best_estimator_, X_train, y_train, cv=5, scoring="accuracy")
cv_skore_text = []
for skore in cv_skore:
    cv_skore_text.append(f"{skore:.2%}")
print(f"Skóre z iterací křížové validace: {', '.join(cv_skore_text)}")
# Testování modelu na neznámých datech
test_score = grid_search.score(X_test, y_test)
print(f"Testovací přesnost: {test_score:.2%}")
# Matice záměn
y_predikce = grid_search.predict(X_test)
matice_zamen = confusion_matrix(y_test, y_predikce)
TN, FP, FN, TP = matice_zamen.ravel()
print(f"TP: {TP}, TN: {TN}, FP: {FP}, FN: {FN}")
print(f"Senzitivita: {recall_score(y_test, y_predikce):.2%}, "
      f"Specificita: {recall_score(y_test, y_predikce, pos_label=0):.2%}, "
      f"PPV: {precision_score(y_test, y_predikce):.2%}")