# Importy
import pandas as pd
from scipy.stats import pearsonr

# Načtení dat
data_cetnosti = pd.read_csv("cetnosti_dle_opl.csv")
data_index = pd.read_excel("Index-sociálního-vyloučení-2023.xlsx")
# Omezení dat na tři sloupce - kraj, obyvatelstvo, index
data_index = data_index[["Název kraj",
                         "Počet obyvyatel - starších 15 let (k 31. 12. 2023)",
                         "Index soc. vyloučení 2023 (0-30 bodů)"]]
# Přejmenování sloupců pro praktičtější práci
data_index.columns = ["kraj", "pocet_obyvatel", "index"]
# Seskupení dat podle krajů a spočtení váženého průměru indexu sociálního vyloučení
lambda_funkce = lambda x: (x["index"] * x["pocet_obyvatel"]).sum() / x["pocet_obyvatel"].sum()
data_index = data_index.groupby("kraj").apply(lambda_funkce)
data_index = data_index.reset_index()
data_index.columns = ["kraj", "vazeny_index"]
# Odstranění dat pro CÚ Praha Ruzyně
data_cetnosti = data_cetnosti[data_cetnosti["Celni_Urad"] != "CÚ Praha Ruzyně"]
# Odstranění CÚ pro ve sloupci Celni_Urad
data_cetnosti["Celni_Urad"] = data_cetnosti["Celni_Urad"].apply(lambda x: x.replace("CÚ pro ", ""))
print(data_cetnosti["Celni_Urad"].unique())