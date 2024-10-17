## Importy
import pandas as pd
import numpy as np
import pickle
import seaborn as sns
from matplotlib import pyplot as plt

# scikit-learn modely pro klasifikaci
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# scikit-learn rozdeleni dat a predzpracovani
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score
from sklearn.metrics import matthews_corrcoef, make_scorer

# imbalanced-learn knihovna pro praci s nevyvazenymi datasety
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import NearMiss

## Nahrani dat a zakladni analyza
data = pd.read_csv("creditcard.csv")
# Rozmery tabulky
print(f"Dimenze dat: {data.shape}")
# Prehled sloupcu
print(f"Sloupce: {(', ').join(data.columns.tolist())}")

# Datove typy
print("\n-----Datove typy-----")
print(data.info())

# Informace o datech
print("\n-----Informace o datech-----")
pd.set_option("display.max_columns", None) # potlaceni omezeni poctu zobrazenych sloupcu
print(data.describe().T)

print("\nZ dat vidime, ze jsou vyrazne nevyvazene jednotlive tridy:")
print(f"-\tpocet vzorku tridy 1 (podezrele transakce): {data['Class'].value_counts().loc[1]}")
print(f"-\tpocet vzorku tridy 0 (normalni transakce): {data['Class'].value_counts().loc[0]}")
pomer_trid = data['Class'].value_counts().loc[1] / data['Class'].value_counts().loc[0]
print(f"-\tpomer mezi tridami 1/0: {pomer_trid:.4%}")

# # Korelacni matice
# korelacni_matice = data.corr()
# plt.figure(figsize=(30, 30))
# sns.heatmap(korelacni_matice, annot=True, annot_kws={"size": 10}, cbar=False, fmt=".2f")
# # plt.show()
# # Boxploty
sloupce_priznaky = data.columns.tolist()
sloupce_priznaky.remove("Class")
# for sloupec in sloupce_priznaky:
#     plt.figure()
#     sns.boxplot(data, x="Class", y=sloupec)
#     plt.gca().set_title(f"Box plot pro sloupec {sloupec} vs. Class")
# plt.show()

# Rozdeleni dat na trenovaci a testovaci
X_train, X_test, y_train, y_test = train_test_split(data[sloupce_priznaky],
                                                    data["Class"], random_state=42, test_size=0.2)
print("\nPomery mezi tridami v rozdelenych datovych sadach:")
print(f"-\ttrenovaci: {y_train.value_counts().loc[1] / y_train.value_counts().loc[0]:.4%}")
print(f"-\ttestovaci: {y_test.value_counts().loc[1] / y_test.value_counts().loc[0]:.4%}")

# Vyber modelu
modely = {
    "logisticka_regrese": LogisticRegression(max_iter=1000),
    "SVC": SVC(max_iter=1000),
    "k_nejblizsich_sousedu": KNeighborsClassifier(),
    "rozhodovaci_strom": DecisionTreeClassifier()
}

# Vyber metrik pro hodnoceni kvality klasifikace
# Metrika pro specificitu - mira uspesne klasifikace nulove tridy
def specificita(y_test, y_pred):
    return recall_score(y_test, y_pred, pos_label=0)
metriky = {
    "ACC": "accuracy",
    "UAR": "balanced_accuracy",
    "SEN": "recall",
    # Vlastni metrika
    "SPE": make_scorer(specificita, greater_is_better=True)
}

# # Natrenovani jednotlivych modelu
# for nazev_modelu, model in modely.items():
#     pipeline = Pipeline([
#         ("skalovac", RobustScaler()),
#         (nazev_modelu, model)
#     ])
#
#     grid_search = GridSearchCV(pipeline, {}, cv=5, scoring=metriky, refit="ACC",
#                                n_jobs=-1)
#     grid_search.fit(X_train, y_train)
#     print(f"\n-----Testovany model: {nazev_modelu}-----")
#     print(f"Vysledne metriky:")
#     for metrika in metriky.keys():
#         print(f"-\t{metrika}: {grid_search.cv_results_[f'mean_test_{metrika}'][0]:.2%}")

# Balancovani pomoci prevzorkovani (vytvoreni syntetickych vzorku minoritni tridy)
prevzorkovac = SMOTE()
X_prevzorkovane, y_prevzorkovane = prevzorkovac.fit_resample(X_train, y_train)
print("\nPrevzorkovani vede ke zvetseni datasetu tak, aby byly vyvazene pocty vzorku"
      " v jednotlivych tridach")
print(f"Velikost prevzorkovaneho datasetu: {X_prevzorkovane.shape}")
pomer_trid_prevzorkovane = y_prevzorkovane.value_counts().loc[1] / y_prevzorkovane.value_counts().loc[0]
print(f"Pomery poctu vzorku v tridach: {pomer_trid_prevzorkovane:.1%}")

