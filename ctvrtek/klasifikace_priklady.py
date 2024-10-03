import pandas as pd
from sklearn.preprocessing import StandardScaler # Škálování dat na stejný interval
# Pipeline pro automatizaci předzpracování dat a trénování
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split # Funkce pro rozdělení datasetu
from sklearn.svm import SVC # Support Vector Machine model
from sklearn.tree import DecisionTreeClassifier # Rozhodovací strom
from sklearn.ensemble import RandomForestClassifier # Náhodný les
from sklearn.metrics import accuracy_score, recall_score, precision_score, roc_curve
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

# Vytvoření pipeline pro SVM
pipeline = Pipeline([
    ('scaler', StandardScaler()), # Standardizace dat na stejný interval hodnot
    ('svm', SVC())
])

print("-------------SVM-------------")
pipeline.fit(X_train, y_train) # Natrénování modelu
y_predikce = pipeline.predict(X_test) # Predikce neznámých dat natrénovaným modelem
print(f"Přesnost predikce: {accuracy_score(y_test, y_predikce):.4f}")
print(f"Senzitivita predikce: {recall_score(y_test, y_predikce):.4f}")
print(f"Pozitivní prediktivní hodnota: {precision_score(y_test, y_predikce):.4f}")
print(f"Selektivita predikce: {recall_score(y_test, y_predikce, pos_label=0):.4f}")