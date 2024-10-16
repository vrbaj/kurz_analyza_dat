import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

np.random.seed(42)
pocet_dni = 365
perioda = 30
amplituda_periody = 10
amplituda_sumu = 1

# index dne
time = np.arange(pocet_dni)
# sezonni komponenta
sezonni_komponenta = amplituda_periody * np.sin(2 * np.pi * time / perioda)
# vykreslení sezónní komponenty
plt.plot(time, sezonni_komponenta)
plt.title("Sezónní komponenta")
plt.xlabel("den")
plt.ylabel("Hodnota")

# náhodný šum
hodnoty_sumu = np.random.normal(0, amplituda_sumu, pocet_dni)
# časová řada y = sezonni_komponenta + náhodný šum
casova_rada = sezonni_komponenta + hodnoty_sumu
# vykreslení časové řady s šumem
plt.figure()
plt.plot(time, casova_rada)
plt.title("Časová řada - sezónní komponenta")
# vykreslení autokorelační a parciální autokorelační fukce
plt.figure(figsize=(12, 6))
plt.subplot(121)
plot_acf(casova_rada, ax=plt.gca(), lags=100)
plt.title("Autokorelační funkce")
plt.subplot(122)
plot_pacf(casova_rada, ax=plt.gca(), lags=100)
plt.title("Parciální autokorelační funkce")

# autoregresní časová řada
ar_rada = np.zeros(pocet_dni)
ar_rada[0] = np.random.normal(0, 1)
for t in range(2, pocet_dni):
    ar_rada[t] = 0.8 * ar_rada[t - 1] + np.random.normal(0, 0.1)

# vykreslení autoregresní řady
plt.figure()
plt.plot(ar_rada)
plt.title("AR řada")
plt.xlabel("den")
plt.ylabel("hodnota")

# vykreslení autokorelační a parciální autokorelační fukce
plt.figure(figsize=(12, 6))
plt.subplot(121)
plot_acf(ar_rada, ax=plt.gca(), lags=100)
plt.title("Autokorelační funkce - ar řada")
plt.subplot(122)
plot_pacf(ar_rada, ax=plt.gca(), lags=100)
plt.title("Parciální autokorelační funkce - ar řada")
plt.show()
