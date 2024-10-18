from matplotlib import pyplot as plt
import pandas as pd
import pickle
import seaborn as sns
import numpy as np

# Metriky pro hodnoceni kvality regulace
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score
from sklearn.metrics import confusion_matrix, matthews_corrcoef, roc_curve

# Nacteni dat a vysledku
with open("vysledky.pickle", "rb") as f:
    vysledky = pickle.load(f)

# Seznam pouzitych modelu
modely = ["logisticka_regrese", "SVC_poly", "SVC_linearni", "SVC_ostatni",
          "k_nejblizsich_sousedu", "nahodny_les"]

# Iterace skrz modely a zobrazeni vysledku
fig_roc, ax_roc = plt.subplots(1, 1, figsize=(10, 10))
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
    ax.set_ylabel("Skutecny stav", rotation=90)
    ax.set_xlabel("Predikce")
    fig.savefig(f"{model}_matice_zamen.png")

    if model not in ["k_nejblizsich_sousedu", "nahodny_les"]:
        fpr, tpr, _ = roc_curve(vysledky["y"],
                                vysledky[model]["nastaveni_modelu"].decision_function(vysledky["X"]))
    else:
        fpr, tpr, _ = roc_curve(vysledky["y"],
                                vysledky[model]["nastaveni_modelu"].predict(vysledky["X"]))

    ax_roc.step(fpr, tpr, label=model)
fig_roc.legend()
ax_roc.set_title("ROC krivka pro jednotlive modely")
ax_roc.set_xlabel("mira falesne pozitivnich")
ax_roc.set_ylabel("mira skutecne pozitivnich", rotation=90)
fig_roc.savefig("roc_krivka.png")
plt.show()