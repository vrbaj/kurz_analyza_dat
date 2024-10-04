import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.linear_model import  LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# načtení datasetu
data = pd.read_csv("House_Rent_Dataset.csv")
# hlavička
print(data.head())
# přejmenování sloupců
data.rename(columns={"Posted On": "datum_inzeratu","BHK": "pocet_pokoju",
                     "Rent": "najem", "Size": "plocha", "Floor": "patro",
                     "Area Type": "druh_lokality", "Area Locality": "okres",
                     "City": "mesto", "Furnishing Status": "zarizeno",
                     "Tenant Preferred": "preferovany_najemce", "Bathroom": "koupelny",
                     "Point of Contact": "kontakt"}, inplace=True)
# kontrola přejmenování
print(data.head())
# info
print(data.info())
# zjištění nevalidních hodnot
print(data.isna().sum())
# deskriptivní statistika
print(data.describe())

# vizualizace rozdělení
sns.pairplot(data)


# přehled nájmů
fig = px.histogram(data, x="najem", color_discrete_sequence=px.colors.qualitative.Set3,
                   title="Histogram nájmů")

fig.show()
# boxplot ná
fig = px.box(data, x="najem", title="Boxplot nájmů")
fig.show()
# umístění outlierů
print(np.where(data["najem"] > 1000000))
print(data.shape)
# smazání outlierů
data.drop([1837, 1001], axis=0, inplace=True)
print(data.shape)
# ověření že jsme smazali správné hodnoty
print(np.where(data["najem"] > 1000000))

# analýza počtu pokojů
print(data["pocet_pokoju"].value_counts())

plt.figure()
ax = sns.countplot(x="pocet_pokoju", data=data)

plt.figure()
ax = sns.countplot(x="koupelny", data=data)
plt.show()

fig = px.pie(data.koupelny.value_counts(), values="count", height=700, width=700, color_discrete_sequence=px.colors.sequential.deep,
             title="Koupelny - koláčový graf", names=data.koupelny.value_counts().index)
fig.update_traces(textfont_size=15)
fig.show()

# přehled měst
ax = sns.countplot(x="mesto", data=data)
#plt.show()

fig = px.pie(data.mesto.value_counts(), values="count", height=700, width=700, color_discrete_sequence=px.colors.sequential.deep,
             title="Města - koláčový graf", names=data.mesto.value_counts().index)
fig.show()

# bivariantní analýza
# počet pokojů - nájem
fig, axes = plt.subplots(figsize=(15,10))
sns.boxenplot(x="pocet_pokoju", y="najem", data=data)
plt.title("Boxenplot pro pocet pokojů a najem")

# koupelny - nájem
fig, axes = plt.subplots(figsize=(15,10))
sns.boxenplot(x="koupelny", y="najem", data=data)
plt.title("Boxenplot pro koupelny a najem")
# smazání neužčitečných/problematických sloupečků z tabulky
data = data.drop(["datum_inzeratu", "okres", "patro"], axis=1)
# kontrola hlavičky po smazání
print(data.head())

# korelace pro číselné sloupečky
corr = data[["pocet_pokoju", "najem", "plocha", "koupelny"]].corr()
plt.subplots(figsize=(8, 6))
sns.heatmap(corr, vmax=1, square=False,annot=True)
plt.show()

data = pd.get_dummies(data, columns=["druh_lokality", "mesto", "zarizeno",
                                     "preferovany_najemce", "kontakt"])
print(data.head())
print(data.shape)

# data pro regresi
X = data.drop("najem", axis=1)
y = data["najem"]

X_trenovaci, X_testovaci, y_trenovaci, y_testovaci = train_test_split(X, y,
                                                                      test_size=0.2, random_state=42)