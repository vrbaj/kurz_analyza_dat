import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

# Načtení dat
data = pd.read_csv("diabetes_modified.csv")
print(data.head())

# Informace o datových typech
print(data.info())

# Základní statistika pro jednotlivé sloupce
pd.set_option('display.max_columns', None)
print(data.describe(percentiles=[0.25, 0.5, 0.75]))

# Zjištění řádků obsahující NaN hodnotu
maska = data.isnull().sum(axis=1) # Maska, jež počítá v každém řádku výskyty NaN hodnot
print("Řádky s NaN hodnotou")
print(data[maska > 0][["BMI"]]) # Filtrování řádků podle masky a vrácení pouze sloupce BMI

# Smazání řádků s výskytem NaN hodnot
data_odstranene_nan = data.dropna()
print("Velikost tabulky po odstranění NaN")
print(data_odstranene_nan.shape)
maska = data_odstranene_nan.isnull().sum(axis=1)
print(data_odstranene_nan[maska > 0][["BMI"]])

# Nahrazení NaN hodnotou
prumerne_bmi = data[data.BMI > 0]["BMI"].mean() # Průměrné BMI pro nenulové hodnoty
data["BMI"] = data["BMI"].fillna(prumerne_bmi) # Nahrazení NaN hodnot průměrem BMI
print(data.isnull().sum()) # Ověření, že ve sloupci BMI nejsou NaN hodnoty

# Korelační matice
korelacni_matice = data.corr()
sns.heatmap(korelacni_matice, annot=True)

# Histogramy jednotlivých sloupců
for sloupec in data.columns:
    plt.figure() # Nové okno (aby se nepřekresloval korelační graf)
    data[sloupec].plot.hist() # Zvolení sloupce a vytvoření histogramu
    plt.title(f"Histogram pro {sloupec}")

# Histogram pomocí seaborn
plt.figure()
sns.histplot(data, x="BMI", y="Pregnancies", hue="Outcome", element="step")

# Boxploty (Krabicové grafy)
plt.figure()
plt.title("Boxplot pro BMI")
sns.boxplot(data, x="BMI")

plt.show() # Zobrazení všech oken