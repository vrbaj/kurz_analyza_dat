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
                                                                      test_size=0.2,
                                                                      random_state=42)
print(y_trenovaci.shape)
print(y_testovaci.shape)
y_trenovaci = y_trenovaci.values.reshape(-1, 1)
y_testovaci = y_testovaci.values.reshape(-1, 1)

# škálování dat
from sklearn.preprocessing import StandardScaler
transformace_X = StandardScaler()
transformace_y = StandardScaler()
X_trenovaci = transformace_X.fit_transform(X_trenovaci)
y_trenovaci = transformace_y.fit_transform(y_trenovaci)
# POZOR NIKDY NEŠKÁLOVAT TRÉNOVACÍ A TESTOVACÍ DATA DOHROMADY!!!!! DATALEAKAGE
X_testovaci = transformace_X.transform(X_testovaci)
y_testovaci = transformace_y.transform(y_testovaci)

# lineární regrese
linearni_model = LinearRegression()
linearni_model.fit(X_trenovaci, y_trenovaci)
linearni_model_predikce = linearni_model.predict(X_testovaci)

mae_lm = mean_absolute_error(y_testovaci, linearni_model_predikce)
mse_lm = mean_squared_error(y_testovaci, linearni_model_predikce)
rmse_lm = np.sqrt(mse_lm)
print(f"Střední absolutní chyba lin. modelu {mae_lm}")
print(f"Střední kvadratická chyba lin. modelu {mse_lm}")
print(f"RMSE lineárního modelu {rmse_lm}")

# regresní rozhodovací strom
dt_model = DecisionTreeRegressor(random_state=42)
dt_model.fit(X_trenovaci, y_trenovaci)
dt_model_predikce = dt_model.predict(X_testovaci)

mae_dt = mean_absolute_error(y_testovaci, dt_model_predikce)
mse_dt = mean_squared_error(y_testovaci, dt_model_predikce)
rmse_dt = np.sqrt(mse_dt)
print(f"Střední absolutní chyba dt modelu {mae_dt}")
print(f"Střední kvadratická chyba dt modelu {mse_dt}")
print(f"RMSE dt modelu {rmse_dt}")

# SVR
svr_model = SVR()
svr_model.fit(X_trenovaci, y_trenovaci)
svr_model_predikce = svr_model.predict(X_testovaci)

mae_svr = mean_absolute_error(y_testovaci, svr_model_predikce)
mse_svr = mean_squared_error(y_testovaci, svr_model_predikce)
rmse_svr = np.sqrt(mse_svr)
print(f"Střední absolutní chyba svr modelu {mae_svr}")
print(f"Střední kvadratická chyba svr modelu {mse_svr}")
print(f"RMSE svr modelu {rmse_svr}")


