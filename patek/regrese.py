import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

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
print(data.koupelny.value_counts())
fig = px.pie(data.koupelny.value_counts(), values="count", height=700, width=700, color_discrete_sequence=px.colors.sequential.deep,
             title="Koupelny - koláčový graf")
fig.update_traces(textfont_size=15)
fig.show()

#plt.show()