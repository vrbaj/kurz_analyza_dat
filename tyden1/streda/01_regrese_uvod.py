import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


# datová sada
data = {"plocha": [150, 250, 180, 220, 320],
        "patro": [3, 4, 3, 4, 5],
        "vzdalenost": [10, 5, 8, 15, 3],
        "cena": [300000, 500000, 360000, 480000, 610000]}

df = pd.DataFrame(data)
print(df.head())
X = df[["plocha", "patro", "vzdalenost"]]
y = df["cena"]
print("vlastnosti")
print(X)
print("cena")
print(y)
# rozdělení dat na trénovací a testovací
X_trenovaci, X_testovaci, y_trenovaci, y_testovaci = train_test_split(X, y, test_size=0.2, random_state=42)
print(X_trenovaci.shape)
linearni_model = LinearRegression()  # model lineární regrese
linearni_model.fit(X_trenovaci, y_trenovaci)  # trénovaní modelu
print(linearni_model.coef_)
y_predikce = linearni_model.predict(X_testovaci)
print(f"Predikovaná cena - {y_predikce}, skutečná cena - {y_testovaci}")
absolutni_chyba_predikce = mean_absolute_error(y_testovaci, y_predikce)
print(f"Střední absolutní chyba predikce je {absolutni_chyba_predikce}")
