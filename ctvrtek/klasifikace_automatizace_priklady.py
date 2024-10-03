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