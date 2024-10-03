import pandas as pd
from sklearn.preprocessing import StandardScaler # Škálování dat na stejný interval
# Pipeline pro automatizaci předzpracování dat a trénování
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split # Funkce pro rozdělení datasetu
from sklearn.svm import SVC # Support Vector Machine model
from sklearn.tree import DecisionTreeClassifier # Rozhodovací strom
from sklearn.ensemble import RandomForestClassifier # Náhodný les


# Nahrání dat
data = pd.read_csv("klasifikace_balancovany.csv")
# print(data.head())
print(data.info())
# Přejmenování prvního sloupce na "Vystup"
nazvy_sloupcu = data.columns.tolist() # Uložení názvy sloupců jako seznam
nazvy_sloupcu[0] = "Vystup" # Přejmenování prvního sloupce na "Vystup"
data.columns = nazvy_sloupcu #print Přiřazení změněného seznamu zpět tabulce
