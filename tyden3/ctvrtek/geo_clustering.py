import math
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans, DBSCAN, SpectralClustering
from sklearn.preprocessing import minmax_scale

data = pd.read_csv("ciste_opl.csv")


for jednotka in data["Merna_jednotka"].unique():
  for opl in data[data["Merna_jednotka"]==jednotka][
                  "Druh_OPL"].unique():
    aktualni_vysek = data.loc[
      (data["Druh_OPL"]==opl) &
      (data["Merna_jednotka"]==jednotka), 
      "Mnoz_v_Porušení"]
    aktualni_vysek = \
      minmax_scale(
        aktualni_vysek
          .apply(lambda x: math.log(x-aktualni_vysek.min()+1))
      )
    data.loc[
      (data["Druh_OPL"]==opl) &
      (data["Merna_jednotka"]==jednotka), 
      "Mnoz_v_Porušení"] = aktualni_vysek
print(data["Mnoz_v_Porušení"].describe())

training_data = data[["Cas_Zjisteni","Mesic", "Mnoz_v_Porušení","den_v_tydnu"]]
for col in training_data.columns:
  training_data[col] = minmax_scale(training_data[col])

for col in ["Misto_kontoly","Druh_vozidla","Stat","Pohlavi_porusitele",
            "Merna_jednotka","Druh_OPL"]:
  training_data = pd.concat([training_data,
                             pd.get_dummies(data[col]).astype(int)],
                             axis = 1)

print("#"*50)
print(training_data.shape)
print(training_data.columns)

print(training_data.describe())

# KMeans
kmeans = KMeans(n_clusters=12, random_state=42)
data["cislo_klastru"] = kmeans.fit_predict(training_data)
print(data["cislo_klastru"].value_counts())

# Zobrazení podle souřadnic
gdf_data = (gpd.read_file("kraje.json")
               .sort_values("id",ascending=False))
ax = gdf_data.plot(color="lightgray", edgecolor="black")
plt.show()