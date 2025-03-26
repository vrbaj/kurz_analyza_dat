from pathlib import Path
import pandas as pd

zaverka = pd.read_excel(Path(".", "mikro", "01a.xlsx"))
#print(zaverka.head())
#print(zaverka.columns)
#print(zaverka["Nazev Polozky"])
sloupce_smazat = [sloupec for sloupec in zaverka.columns if sloupec.startswith("Unnamed")]
#print(sloupce_smazat)
zaverka.drop(sloupce_smazat, axis=1, inplace=True)
print(zaverka.head())
print(zaverka["Nazev Polozky"])
data_pro_ar = zaverka.loc[zaverka["Nazev Polozky"] == "HVzaUcetniObdobi"].copy()
print(data_pro_ar)
data_pro_ar.drop(["Nazev Polozky"], axis=1, inplace=True)
print("Data pro AR po smazání nenumerických hodnot")
print(data_pro_ar)
X_ar = data_pro_ar.to_numpy()
print(X_ar)
AR_trenovaci_data = X_ar[0, 0:-1]
print("Trénovací data pro AR model")
print(AR_trenovaci_data)
AR_testovaci_data = X_ar[0, -1]
print("Testovací data pro AR model")
print(AR_testovaci_data)