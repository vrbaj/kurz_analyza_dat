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
