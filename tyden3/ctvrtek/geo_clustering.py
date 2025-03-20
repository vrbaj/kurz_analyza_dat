import math
import pandas as pd
import geopandas
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
print(data["Mnoz_v_Porušení"].describe())