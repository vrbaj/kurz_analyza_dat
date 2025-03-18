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
    # Graf s činnostmi
    fig, ax = plt.subplots()
    sns.barplot(top_cetnost_kc, x="Kontrolni_Cinnost", y="cetnost", hue="Poruseni", ax=ax)
    ax.tick_params(axis="x", labelrotation=90)
    ax.set_title(celni_urad)
    plt.tight_layout()
plt.show()
