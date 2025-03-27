from pathlib import Path
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
from matplotlib import pyplot as plt

TYP_FIRMY = "mikro"
#tabulka s výsledky predikcí pro jednotlivé firmy
vysledky_predikci = pd.DataFrame(columns=["soubor", "chyba_predikce",
                                          "skutecna_hodnota", "predikovana_hodnota",
                                          "relativni_chyba"])
print(vysledky_predikci)
print(vysledky_predikci.columns)

for soubor in Path(".", TYP_FIRMY).iterdir():
    print(f"Zpracovávám závěrku {soubor.name}")
    zaverka = pd.read_excel(soubor)
    #print(zaverka.head())
    #print(zaverka.columns)
    #print(zaverka["Nazev Polozky"])
    sloupce_smazat = [sloupec for sloupec in zaverka.columns if sloupec.startswith("Unnamed")]
    #print(sloupce_smazat)
    zaverka.drop(sloupce_smazat, axis=1, inplace=True)
    # print(zaverka.head())
    # print(zaverka["Nazev Polozky"])
    data_pro_ar = zaverka.loc[zaverka["Nazev Polozky"] == "HVzaUcetniObdobi"].copy()
    # print(data_pro_ar)
    data_pro_ar.drop(["Nazev Polozky"], axis=1, inplace=True)
    nazvy_roku = data_pro_ar.columns
    # print("Data pro AR po smazání nenumerických hodnot")
    # print(data_pro_ar)
    X_ar = data_pro_ar.to_numpy()
    # print(X_ar)
    AR_trenovaci_data = X_ar[0, 0:-1]
    # print("Trénovací data pro AR model")
    # print(AR_trenovaci_data)
    AR_testovaci_data = X_ar[0, -1]
    # print("Testovací data pro AR model")
    # print(AR_testovaci_data)
    # AR model
    ar_model = ARIMA(AR_trenovaci_data, order=(2, 0, 0))
    try:
        natrenovany_model = ar_model.fit()
        predikce = natrenovany_model.forecast(steps=1)[0]
    except np.linalg.LinAlgError:
        predikce = np.inf
    chyba_predikce = AR_testovaci_data - predikce
    print(f"absolutní chyba predikce: {chyba_predikce} - "
          f"očekávaná hodnota: {AR_testovaci_data} - "
          f"predikce: {predikce}")
    relativni_chyba_predikce = (predikce - AR_testovaci_data) / (AR_testovaci_data + 1e-6)
    novy_radek_vysledku = pd.DataFrame([[soubor.name, chyba_predikce, AR_testovaci_data,
                                         predikce, relativni_chyba_predikce]],
                                       columns=vysledky_predikci.columns)
    vysledky_predikci = pd.concat([vysledky_predikci, novy_radek_vysledku])
    if not np.isinf(predikce):
        plt.figure()
        plt.title(soubor.name)
        plt.plot(nazvy_roku, X_ar[0, :])
        plt.plot(nazvy_roku[-1], predikce, marker="o", markersize=5, color="red")
        plt.xlabel("ROK")
#plt.show()
infs = vysledky_predikci[(vysledky_predikci == np.inf).any(axis=1)]
print(infs)
vysledky_predikci.replace(np.inf, np.nan, inplace=True)
vysledky_predikci.dropna(inplace=True)
vysledky_predikci.set_index("soubor")
vysledky_predikci.plot(x="soubor", y="chyba_predikce", kind="bar")
vysledky_predikci.to_csv(f"{TYP_FIRMY}_ar_predikce.csv")
plt.show()
