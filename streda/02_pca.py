import matplotlib.pyplot as plt # knihovna pro vizualizaci
import seaborn as sns # pro zobrazení korelace a distribuce
import numpy as np
import pandas as pd
from sklearn import datasets # kosatcový dataset
from sklearn.decomposition import PCA # PCA analýza
from sklearn.preprocessing import StandardScaler

# načtení datasetu
iris = datasets.load_iris()
print(dir(iris))
print(iris.data)
# velikost dat
print(iris.data.shape)
print(iris.target.shape)

# názvy features
print(iris.feature_names)
print(iris.target_names)

# vytvoření X, y
X = iris.data
y = iris.target
# škálování dat
X = StandardScaler().fit_transform(X)

dataframe = pd.DataFrame(X, columns=iris.feature_names)
dataframe["target"] = y
# dataframe["target"].replace({0:iri
# s.target_names[0], 1:iris.target_names[1], 2:iris.target_names[2]}, inplace=True)


# korelační matice
fig_heatmap = plt.figure(figsize=(15, 8.5))
fig_heatmap.suptitle("Korelační matice", fontsize=25, fontweight="bold")
sns.heatmap(dataframe.corr(method="pearson"), cmap='crest', linewidths=0.5, annot=True)


# distribuce dat
sns_matrix = sns.pairplot(dataframe, hue="target")
sns_matrix.fig.subplots_adjust(top=.9)
sns_matrix.fig.suptitle("Matrix plot pro všechny kombinace vlastností")


# Custom distribution plot matrix
fig1, axes1 = plt.subplots(2,3, figsize=(18,10.5))
axes1 = axes1.reshape(-1)
fig1.suptitle("Porovnání různých kombinací vlastností pro skupiny kosatců", fontsize = 20)
COUNT = 0
for i in range(0, len(iris.feature_names) - 1):
    for j in range(i + 1, len(iris.feature_names)):
        # Scatter plot
        axes1[COUNT].scatter(X[:, i], X[:, j], c=y, edgecolor="k", s=60)
        # nastavení názvů
        axes1[COUNT].set_xlabel(iris.feature_names[i], fontweight="bold")
        axes1[COUNT].set_ylabel(iris.feature_names[j], fontweight="bold")
        # limit os
        axes1[COUNT].set_xlim([X[:, i].min() - 0.1, X[:, i].max() + 0.1])
        axes1[COUNT].set_ylim([X[:, j].min() - 0.1, X[:, j].max() + 0.1])
        # popisky os
        axes1[COUNT].set_xticks(np.linspace(X[:, i].min() - 0.1, X[:, i].max() + 0.1, 5))
        axes1[COUNT].set_yticks(np.linspace(X[:, j].min() - 0.1, X[:, j].max() + 0.1, 5))
        # zapnutí mřížky
        axes1[COUNT].grid(which="major", color="k", linestyle="--")

        COUNT += 1

# PCA Analyses
# 1 komponenta
pca1 = PCA(n_components=1)
pca1_x = pca1.fit_transform(X)
print(f"Vysvětlená variance 1 komponentou- {pca1.explained_variance_ratio_}")
# 2 komponenty
pca2 = PCA(n_components=2)
pca2_x = pca2.fit_transform(X)
print(f"Vysvětlená variance 2 komponenty- {pca2.explained_variance_ratio_}")
# 3 komponenty
pca3 = PCA(n_components=3)
pca3_x = pca3.fit_transform(X)
print(f"Vysvětlená variance 3 komponenty- {pca3.explained_variance_ratio_}")
# vizualizace dat
fig_pc = plt.figure(figsize=(18, 6))
fig_pc.suptitle("Porovnání transformací pro různé počty komponent", fontweight="bold", fontsize=20)
fig_pc.subplots_adjust(top=0.835, left=0.023, right=0.982, hspace=0.106, wspace=0.232)
# PC 1
# grafy
ax_empty = plt.subplot(331)
for direction in ['top', 'bottom', 'left', 'right']:
    ax_empty.spines[direction].set_visible(False)
ax_empty.set_xticks([])
ax_empty.set_yticks([])
ax_empty.set_title("Transformace pro 1 komponentu")
# True plots
axes_pc1 = plt.subplot(334)
axes_pc2 = plt.subplot(132)
axes_pc3 = plt.subplot(133, projection="3d")
# plot výsledků transformace
axes_pc1.scatter(pca1_x, np.zeros(pca1_x.shape), c=y)
axes_pc2.scatter(pca2_x[:,0], pca2_x[:,1], c=y)
axes_pc3.scatter(pca3_x[:,0], pca3_x[:,1], pca3_x[:,2], c=y)
# print(pca.explained_variance_ratio_)
# titulky grafů
axes_pc2.set_title("Transformace pro 2 komponenty")
axes_pc3.set_title("Transformace pro 3 komponenty")
# mřízka
axes_pc1.set_xticks(np.linspace(min(axes_pc1.get_xlim()), max(axes_pc1.get_xlim()), 5))
axes_pc1.set_yticks(np.linspace(min(axes_pc1.get_ylim()), max(axes_pc1.get_ylim()), 5))
axes_pc1.grid(which="major", linestyle="--", color="k")
axes_pc2.set_xticks(np.linspace(min(axes_pc2.get_xlim()), max(axes_pc2.get_xlim()), 5))
axes_pc2.set_yticks(np.linspace(min(axes_pc2.get_ylim()), max(axes_pc2.get_ylim()), 5))
axes_pc2.grid(which="major", linestyle="--", color="k")
axes_pc3.set_xticks(np.linspace(min(axes_pc3.get_xlim()), max(axes_pc3.get_xlim()), 5))
axes_pc3.set_yticks(np.linspace(min(axes_pc3.get_ylim()), max(axes_pc3.get_ylim()), 5))
axes_pc3.set_zticks(np.linspace(min(axes_pc3.get_zlim()), max(axes_pc3.get_zlim()), 5))
# popisky
axes_pc1.set_xlabel("PC 1")
axes_pc2.set_xlabel("PC 1")
axes_pc2.set_ylabel("PC 2")
axes_pc3.set_xlabel("PC 1")
axes_pc3.set_ylabel("PC 2")
axes_pc3.set_zlabel("PC 3")
# pro 1 komponentu 1D plot
axes_pc1.axhline(y=0, c="k", linestyle="-", linewidth=1)
axes_pc1.set_yticks([])
axes_pc1_y_limit = max(axes_pc1.get_xlim()) - min(axes_pc1.get_xlim())
axes_pc1.set_ylim([-0.05*axes_pc1_y_limit, 0.05*axes_pc1_y_limit])
axes_pc1.set_aspect("equal")
for direction in ['top', 'bottom']:
    axes_pc1.spines[direction].set_visible(False)


# vysvětlená variance - graf úpatí
fig_pcvar = plt.figure(figsize=(18,6))
fig_pcvar.suptitle("Explained Variance v závislosti na počtu hlavních komponent", fontweight="bold")
ax_pcvar = plt.subplot(121)
ax_pccumvar = plt.subplot(122)
## Defining plot values
pca_var = pca3.explained_variance_ratio_
pca_cumvar = np.cumsum(pca_var)

## Plotting bar charts
ax_pcvar.bar(['PC1', 'PC2', 'PC3'], pca_var, edgecolor="k", linestyle="--")
ax_pccumvar.bar(['PC1', 'PC2', 'PC3'], pca_cumvar, edgecolor="k", linestyle="--")

## doplnění hodnot do sloupcových grafů
for i, pc_vars in enumerate(zip(pca_var, pca_cumvar)):
    ax_pcvar.text(i, pc_vars[0] + 0.01 * max(pca_var), f"{pc_vars[0]:.2%}", ha ='center')
    ax_pccumvar.text(i, pc_vars[1] + 0.01 * min(pca_cumvar), f"{pc_vars[1]:.2%}", ha='center')

## popisky
ax_pcvar.set_xlabel("Vyvětlená Variance")
ax_pccumvar.set_xlabel("Kumulativní vysvětlená Variance")

## čísla na osách
yticks = [f"{i:.0%}" for i in np.linspace(0,1,6)]
ax_pcvar.set_yticks(np.linspace(0,1,6), yticks)
ax_pccumvar.set_yticks(np.linspace(0,1,6), yticks)

plt.show()