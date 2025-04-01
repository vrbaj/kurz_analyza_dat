from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from matplotlib import pyplot as plt

TYP_FIRMY = "mikro"
#tabulka s výsledky predikcí pro jednotlivé firmy
vysledky_predikci = pd.DataFrame(columns=["soubor", "chyba_predikce",
                                          "skutecna_hodnota", "predikovana_hodnota",
                                          "relativni_chyba"])
print(vysledky_predikci)
print(vysledky_predikci.columns)

for soubor in Path(".", TYP_FIRMY).iterdir():
    print(f"Zpracovávám {soubor}")
    zaverka = pd.read_excel(soubor)
    sloupce_smazat = [sloupec for sloupec in zaverka.columns if sloupec.startswith("Unnamed")]
    zaverka.drop(sloupce_smazat, axis=1, inplace=True)
    data_pro_ar = zaverka.loc[zaverka["Nazev Polozky"] == "HVzaUcetniObdobi"].copy()
    data_pro_ar.drop(["Nazev Polozky"], axis=1, inplace=True)
    # print(data_pro_ar.head())
    data_pro_x = zaverka[zaverka["Nazev Polozky"].isin(["ProvozniVysledekHospodareni",
                                                        "CistyObratZaUO"])].copy()
    data_pro_x = zaverka[zaverka["Nazev Polozky"].isin(["ProvozniVysledekHospodareni"])].copy()
    data_pro_x.drop(["Nazev Polozky"], axis=1, inplace=True)
    # print(data_pro_x.head())
    # trénování ARX modelu
    X_ar = data_pro_ar.to_numpy()
    EX_ar = data_pro_x.to_numpy()
    AR_trenovaci_data = X_ar[0, 0:-1]
    EX_trenovaci_data = EX_ar[:, 0:-1]
    AR_testovaci_data = X_ar[0, -1]
    EX_testovaci_data = EX_ar[:, -1]
    #print(AR_trenovaci_data.shape)
    #print(EX_trenovaci_data.shape)
    model = ARIMA(AR_trenovaci_data, exog=EX_trenovaci_data.T, order=(2, 0, 0))
    try:
        natrenovany_model = model.fit()
        predikce = natrenovany_model.forecast(steps=1, exog=EX_testovaci_data.T)[0]
        #print(f"Predikce: {predikce}, skutečnost: {AR_testovaci_data}")
    except np.linalg.LinAlgError:
        predikce = np.inf
    chyba_predikce = predikce - AR_testovaci_data
    relativni_chyba_predikce = chyba_predikce / (AR_testovaci_data + 1e-6)
    novy_radek = pd.DataFrame([[soubor.name, chyba_predikce, AR_testovaci_data, predikce,
                                relativni_chyba_predikce]],
                              columns=vysledky_predikci.columns)
    vysledky_predikci = pd.concat([vysledky_predikci, novy_radek])
    if not np.isinf(predikce):
        plt.figure()
        plt.title(soubor.name)
        roky = data_pro_ar.columns
        barva = "red" if chyba_predikce > 0 else "green"
        plt.plot(roky, data_pro_ar.T)
        plt.plot(roky[-1], predikce, marker="o", color=barva, markersize=5)
        plt.xlabel("ROKY")
infs = vysledky_predikci[(vysledky_predikci == np.inf).any(axis=1)]
print(infs)
vysledky_predikci.replace(np.inf, np.nan, inplace=True)
vysledky_predikci.dropna(inplace=True)
vysledky_predikci.set_index("soubor")
vysledky_predikci.plot(x="soubor", y="chyba_predikce", kind="bar")
vysledky_predikci.to_csv(f"{TYP_FIRMY}_arx_predikce.csv")
plt.show()