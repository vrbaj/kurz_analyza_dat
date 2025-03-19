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
    "Náhodný les": {"max_depth": [5, 10, 20, None],
                    "min_samples_split": [2, 5, 10, 20],
                    "max_features": ["sqrt", "log2", None],
                    "n_estimators": [5, 11, 21],
                    "max_samples": [0.4, 0.6, 0.8, 1]
                        },
}