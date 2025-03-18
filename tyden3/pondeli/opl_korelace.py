# Importy
import pandas as pd
from scipy.stats import pearsonr

# Načtení dat
data_cetnosti = pd.read_csv("cetnosti_dle_opl.csv")
data_index = pd.read_excel("Index-sociálního-vyloučení-2023.xlsx")
data_index = data_index[["Název kraj",
                         "Počet obyvyatel - starších 15 let (k 31. 12. 2023)",
                         "Index soc. vyloučení 2023 (0-30 bodů)"]]

