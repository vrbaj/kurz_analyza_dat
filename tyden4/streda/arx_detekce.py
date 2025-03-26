from pathlib import Path
import pandas as pd

zaverka = pd.read_excel(Path(".", "mikro", "01a.xlsx"))
sloupce_smazat = [sloupec for sloupec in zaverka.columns if sloupec.startswith("Unnamed")]
zaverka.drop(sloupce_smazat, axis=1, inplace=True)
data_pro_ar = zaverka.loc[zaverka["Nazev Polozky"] == "HVzaUcetniObdobi"].copy()
data_pro_ar.drop(["Nazev Polozky"], axis=1, inplace=True)
print(data_pro_ar.head())
data_pro_x = zaverka[zaverka["Nazev Polozky"].isin(["ProvozniVysledekHospodareni",
                                                    "CistyObratZaUO"])].copy()
data_pro_x.drop(["Nazev Polozky"], axis=1, inplace=True)
print(data_pro_x.head())
# trénování ARX modelu