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
# Nahrazení Hl. město Prahu za Hlavní město Praha
data_cetnosti["Celni_Urad"] = data_cetnosti["Celni_Urad"].apply(lambda x: x.replace("Hl. město Prahu", "Hlavní město Praha"))

# Sloučení tabulek s počty kontrol a s indexem soc. vyloučení
data_sloucena = data_index.merge(data_cetnosti, left_on="kraj", right_on="Celni_Urad",
                                 how="left")
# Odstranění sloupce Celni_Urad
data_sloucena.drop(columns=["Celni_Urad"], inplace=True)

# Iterace skrz typy OPL
for opl in data_sloucena.columns[2:]:
    koeficient, phodnota = pearsonr(data_sloucena["vazeny_index"], data_sloucena[opl])
    print(f"Pro {opl}: korelační koeficient {koeficient:.4f}, p-hodnota {phodnota:.4f}.")

# Sloučení Konopí sušiny a živých rostlin a spočtení korelace
data_konopi = data_sloucena["Konopí (živé rostliny)"] + \
              data_sloucena["Konopí (sušina - marihuana)"]
print(f"Pro sloučené konopí: {pearsonr(data_sloucena['vazeny_index'], data_konopi)}.")

# Sloučení všech typů drog pro korelaci mezi počtem kontrol a indexem soc. vyloučení
kontroly_celkem = data_sloucena.iloc[:, 2:].sum(axis=1)
koeficient, phodnota = pearsonr(data_sloucena["vazeny_index"], kontroly_celkem)
print(f"Pro celkové počty kontrol: korelační koef. {koeficient:.4f}, p-hodnota {phodnota:.4f}.")

# pd.set_option("display.max_columns", None)
# print(data_sloucena)