## Importy
import pandas as pd
import numpy as np
import pickle
import seaborn as sns
from matplotlib import pyplot as plt

# scikit-learn modely pro klasifikaci
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# scikit-learn rozdeleni dat a predzpracovani
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score
from sklearn.metrics import matthews_corrcoef, make_scorer

# imbalanced-learn knihovna pro praci s nevyvazenymi datasety
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import NearMiss

## Nahrani dat a zakladni analyza
data = pd.read_csv("creditcard.csv")
# Rozmery tabulky
print(f"Dimenze dat: {data.shape}")
# Prehled sloupcu
print(f"Sloupce: {(', ').join(data.columns.tolist())}")

# Datove typy
print("\n-----Datove typy-----")
print(data.info())

# Informace o datech
print("\n-----Informace o datech-----")
pd.set_option("display.max_columns", None) # potlaceni omezeni poctu zobrazenych sloupcu
print(data.describe().T)

print("\nZ dat vidime, ze jsou vyrazne nevyvazene jednotlive tridy:")
print(f"-\tpocet vzorku tridy 1 (podezrele transakce): {data['Class'].value_counts().loc[1]}")
print(f"-\tpocet vzorku tridy 0 (normalni transakce): {data['Class'].value_counts().loc[0]}")
pomer_trid = data['Class'].value_counts().loc[1] / data['Class'].value_counts().loc[0]
print(f"-\tpomer mezi tridami 1/0: {pomer_trid:.4%}")