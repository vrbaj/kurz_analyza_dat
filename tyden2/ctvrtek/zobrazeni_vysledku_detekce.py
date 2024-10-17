from matplotlib import pyplot as plt
import pandas as pd
import pickle
import seaborn as sns
import numpy as np

# Metriky pro hodnoceni kvality regulace
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score
from sklearn.metrics import confusion_matrix, matthews_corrcoef

# Nacteni dat a vysledku
with open("vysledky.pickle", "rb") as f:
    vysledky = pickle.load(f)

# Seznam pouzitych modelu
modely = ["logisticka_regrese", "SVC_poly", "SVC_linearni", "SVC_ostatni",
          "k_nejblizsich_sousedu", "nahodny_les"]

# Iterace skrz modely a zobrazeni vysledku
for model in modely:
    # Predikce na neznamych datech
    y_pred = vysledky[model]["nastaveni_modelu"].predict(vysledky["X"])
    # Metriky pro neznama data
    print(f"\n-----Model: {model}-----")
    print(f"-\tACC: {accuracy_score(vysledky['y'], y_pred):.2%}")
    print(f"-\tUAR: {balanced_accuracy_score(vysledky['y'], y_pred):.2%}")
    print(f"-\tSEN: {recall_score(vysledky['y'], y_pred):.2%}")
    print(f"-\tSPE: {recall_score(vysledky['y'], y_pred, pos_label=0):.2%}")
    print(f"-\tMCC: {matthews_corrcoef(vysledky['y'], y_pred):.2%}")

    # Matice zamen
    matice_zamen = confusion_matrix(vysledky['y'], y_pred)
    # Vykresleni matice zamen
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    sns.heatmap(matice_zamen, ax=ax, annot=True, fmt=".0f", cbar=False)
    ax.set_title(f"Matice zamen pro model {model}")
    ax.set_ylabel("Predikce", rotation=90)
    ax.set_xlabel("Skutecny stav")

plt.show()