from pathlib import Path
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import balanced_accuracy_score
from sklearn.tree import plot_tree

vysledky = pd.DataFrame(columns=["model", "UAR"])
for data in Path(".", "modely").iterdir():
    deserializovane_data = joblib.load(data)
    print(f"Obsah {data.name} - {deserializovane_data.keys()}")
    X_test = deserializovane_data["data_x"]
    y_test = deserializovane_data["data_y"]
    model = deserializovane_data["model"]
    print(model.get_params())
    y_pred = model.predict(X_test)
    uar = balanced_accuracy_score(y_test, y_pred)
    novy_radek = pd.DataFrame([[data.name, uar]], columns=vysledky.columns)
    vysledky = pd.concat([novy_radek, vysledky], ignore_index=True)
vysledky.sort_values(by="model", ascending=False, inplace=True)
vysledky.reset_index(drop=True, inplace=True)
vysledky_puvodni = pd.read_csv("tabulka_vysledku.csv")
vysledky_puvodni.sort_values(by="Soubor_s_modelem", ascending=False, inplace=True)
vysledky_puvodni.reset_index(drop=True, inplace=True)
# porovnání UAR deserializované modely vs modely trénované a testované ve smyčce
print(vysledky["UAR"].compare(vysledky_puvodni["UAR"]))
print(vysledky["UAR"].equals(vysledky_puvodni["UAR"]))
print("Chyba v UAR --------------------")
print(max(vysledky["UAR"] - vysledky_puvodni["UAR"]))


strom = model.estimators_[0]
plot_tree(strom, proportion=True, feature_names=deserializovane_data["features"])
plt.title("1. strom")
plt.savefig("strom1.png", dpi=1200)

print(model.feature_importances_)
print(deserializovane_data["features"])
for idx, feature in enumerate(model.feature_importances_):
    print(f'{deserializovane_data["features"][idx]} - {feature}')
