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
# Problém s druhem vozidla - chybějící hodnoty
data["Druh_vozidla"] = data["Druh_vozidla"].fillna("nezjištěno")
print(data[pd.isna(data["Druh_vozidla"])].shape)