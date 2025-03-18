# Importy
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

# Celní Úřad - Kontrolní činnost - porušení pro mobilní dohled
# Načtení dat
data = pd.read_pickle("kontroly_ocistene.pkl")
# Filtrace pouze mobilního dohledu
data_md = data[data["Utvar"] == "Mobilní dohled"]
# Iterace přes jednotlivé CÚ
celni_urady = data_md["Celni_Urad"].unique()
for celni_urad in celni_urady:
    # Filtrace dat pro daný CÚ
    data_cu = data_md[data_md["Celni_Urad"] == celni_urad]
    # Celkové četnosti kontrolních činností pro daný CÚ
    pocty_kc = (data_cu["Kontrolni_Cinnost"].value_counts().sort_values(ascending=False)
                .reset_index())
    # Top 20 KČ podle celkové četnosti pro daný CÚ
    top_kc = pocty_kc.head(20)["Kontrolni_Cinnost"].tolist()
    # Sloučení podle KČ a Porušení pro získání četností porušení pro jednotlivé KČ
    cetnost_kc = data_cu.groupby(["Kontrolni_Cinnost", "Poruseni"])["Poruseni"].count()
    cetnost_kc.name = "cetnost"
    cetnost_kc = cetnost_kc.reset_index()
    # Vyfiltrování top 20 KČ
    top_cetnost_kc = cetnost_kc[cetnost_kc["Kontrolni_Cinnost"].isin(top_kc)]
    # Seřazení hodnot sestupně podle četnosti
    # top_cetnost_kc.sort_values("cetnost", ascending=False, inplace=True)
    # Graf s činnostmi
    fig, ax = plt.subplots(figsize=(16, 8))
    sns.barplot(top_cetnost_kc, y="Kontrolni_Cinnost", x="cetnost", hue="Poruseni", ax=ax)
    # Přidání anotací k sloupcům
    for sloupec in ax.containers:
        ax.bar_label(sloupec)
    # Otočení popisků os
    # ax.tick_params(axis="x", labelrotation=90)
    # Doplnění celního úřadu do nadpisu
    ax.set_title(celni_urad)
    # Nastavení logaritmického měřítka
    ax.set_xscale("log")
    plt.tight_layout()
    # Uložení grafu
    fig.savefig(f"graf_kc_{celni_urad}.png")
    # Uložení dat s četnostmi porušení pro CÚ podle KČ
    cetnost_kc.to_csv(f"cetnosti_kc_{celni_urad}.csv")
plt.show()
