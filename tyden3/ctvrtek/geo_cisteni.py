import pandas
import geopandas
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib

df = pandas.read_excel("OPL_VSCHT.xlsx", decimal=",")
print(df.columns)

for col in df.columns:
    if col in ["Cas_Zjisteni"]:
        continue
    print("#"*50)
    print(col, ": ", df[col].unique())