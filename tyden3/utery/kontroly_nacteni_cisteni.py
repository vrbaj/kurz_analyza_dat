# Importy
import pandas as pd

# Načtení dat
data_kontroly = pd.read_excel("Kontroly_VSCHT.xlsx")
data_kontroly.to_pickle("Kontroly_VSCHT.pkl")

