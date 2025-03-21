import math
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans, DBSCAN, SpectralClustering
from sklearn.preprocessing import minmax_scale
from tabulate import tabulate
data = pd.read_csv("ciste_opl.csv")

# Převedení jednotek na nějaké rozumné měřítko
for jednotka in data["Merna_jednotka"].unique():
  for opl in data[data["Merna_jednotka"]==jednotka][
                  "Druh_OPL"].unique():
    # Docasně si uložíme hodnoty, které chceme převést
    aktualni_vysek = data.loc[
      (data["Druh_OPL"]==opl) &
      (data["Merna_jednotka"]==jednotka), 
      "Mnoz_v_Porušení"]
    aktualni_vysek = \
      minmax_scale( # Škálujeme data na interval 0-1
        aktualni_vysek
          .apply(lambda x: math.log(x-aktualni_vysek.min()+1)) 
          # převedeme hodnoty od 0 do hodně na logarimickou škálu
          # (přičteme 1, abychom se vyhnuli log(0))
      )
    data.loc[
      (data["Druh_OPL"]==opl) &
      (data["Merna_jednotka"]==jednotka), 
      "Mnoz_v_Porušení"] = aktualni_vysek # Uložíme zpět do dat

# Zkontrolujeme, zda se nám podařilo převést jednotky
print(data["Mnoz_v_Porušení"].describe())

# Převedeme numerické sloupce na interval 0-1
training_data = data[["Cas_Zjisteni","Mesic", "Mnoz_v_Porušení","den_v_tydnu"]]
for col in training_data.columns:
  training_data[col] = minmax_scale(training_data[col])

# Kategorické sloupce převedeme na one-hot encoding
for col in ["Misto_kontoly","Druh_vozidla","Stat","Pohlavi_porusitele",
            "Merna_jednotka","Druh_OPL"]:
  training_data = pd.concat([training_data,
                             pd.get_dummies(data[col]).astype(int)],
                             axis = 1)

print("#"*50)
print(training_data.shape)
print(training_data.columns)

print(training_data.describe())

# KMeans - vyzkoušíme různé počty klastrů (n_clusters)
#kmeans = KMeans(n_clusters=9, random_state=42)
#data["cislo_klastru"] = kmeans.fit_predict(training_data)
#print(data["cislo_klastru"].value_counts())

# DBSCAN - vyzkoušíme různé hodnoty eps (vzdálenost mezi body)
#          a min_samples (kolik bodů se použije na inicializaci klastru)
dbscan = DBSCAN(eps=0.1, min_samples=15)
data["cislo_klastru"] = dbscan.fit_predict(training_data)
print(data["cislo_klastru"].value_counts())

# Zobrazení dat na mapě, kde každý klastr má jinou barvu
gdf_data = (gpd.read_file("kraje.json")
               .sort_values("id",ascending=False))
ax = gdf_data.plot(color="lightgray", edgecolor="black")
ax.set_title("Mapa")
sns.scatterplot(data,x="OsaY",y="OsaX", hue="cislo_klastru", palette="bright",
                s=15, alpha=0.6, ax=ax, legend=False)

# Spočítáme si statistiky pro každý klastr - střed a poloměr
klastry = pd.DataFrame(columns = ["X","Y","polomer"])
for n_klastru in list(data["cislo_klastru"].unique()):
  aktualni = data[data["cislo_klastru"]==n_klastru]
  x,y = aktualni[["OsaX","OsaY"]].mean()
  polomer = ((aktualni[["OsaX","OsaY"]]-(x,y))
             .apply(lambda x: 
              math.sqrt(x["OsaX"]**2 + x["OsaY"]**2),
             axis = 1)).mean()
  klastry.loc[n_klastru,:] = (x,y,polomer)
print(klastry)

#print(tabulate(data[data["cislo_klastru"]==1],headers="keys"))
#sns.scatterplot(data[data["cislo_klastru"]==1],x="OsaY",y="OsaX", hue="cislo_klastru", palette="bright",
#                s=45, alpha=0.6, ax=ax, legend=False)

# Zobrazíme 3 nejmenší klastry na mapě
klastry = klastry.sort_values("polomer",ascending=True)[:3]
for _,row in klastry.iterrows():
  kruh = matplotlib.patches.Circle(
    xy=(row["Y"],row["X"]),
    radius=row["polomer"],
    fill = False,
    edgecolor = "gray",
    alpha = 0.5,
    lw = 2,
  )
  ax.add_patch(kruh)

data.to_csv("naklastrovana_data.csv",index=False)
plt.show()
