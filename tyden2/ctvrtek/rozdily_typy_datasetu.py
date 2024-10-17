import pickle
import pandas as pd
from matplotlib import pyplot as plt

tabulky_vysledky = []
seznam_nazvy = ["nevybalancovana", "podvzorkovana", "prevzorkovana"]

for nazev in seznam_nazvy:
    with open(f"vysledky_{nazev}_data.pk", "rb") as f:
        vysledek = pickle.load(f)
        # print(vysledek)
        for nazev_modelu, metriky in vysledek.items():
            radek_vysledku = [
                nazev, nazev_modelu, metriky["mean_test_ACC"][0],
                metriky["mean_test_UAR"][0], metriky["mean_test_SEN"][0],
                metriky["mean_test_SPE"][0]
            ]
            tabulky_vysledky.append(radek_vysledku)

df_vysledky = pd.DataFrame(data=tabulky_vysledky,
                           columns=["uprava" ,"nazev_modelu", "ACC",
                                    "UAR", "SEN", "SPE"])
print(df_vysledky.head())
print(f"Rozmery tabulky: {df_vysledky.shape}")

# Vykresleni metrik pro jednotlive modely podle upravy dat
for model in df_vysledky["nazev_modelu"].unique().tolist():
    # Vyfiltrovani radku podle modelu
    df_vysledek_modelu = df_vysledky[df_vysledky["nazev_modelu"] == model].copy()
    # Odstraneni sloupce s nazvem modelu a transpozice tabulky
    df_vysledek_modelu.drop("nazev_modelu", axis=1, inplace=True)
    df_vysledek_modelu = df_vysledek_modelu.T
    # Prirazeni prvniho radku s popisky dat do nazvu sloupcu a odstraneni radku z tabulky
    df_vysledek_modelu.columns = df_vysledek_modelu.iloc[0, :]
    df_vysledek_modelu.drop("uprava", inplace=True)
    # Vykresleni dat a pojmenovani grafu
    df_vysledek_modelu.plot(kind="bar", figsize=(10, 10))
    plt.gca().set_title(f"Vysledky pro {model}")

plt.show()