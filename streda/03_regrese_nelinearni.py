import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
from scipy import optimize
import pylab

H = np.array([2, 5, 7, 10, 14, 19, 26, 31, 34, 38, 45, 52, 53, 60, 65])
PI = np.array([54, 50, 45, 37, 35, 25, 20, 16, 18, 13, 8, 11, 8, 4, 6])
print(H.shape)
print(PI.shape)

plt.scatter(H, PI)  # vykreslení dat
plt.xlabel("H [den]")
plt.ylabel("PI [-]")
plt.grid(True)


# Lineární model PI = H * slope + intercept
linearni_model = stats.linregress(H, PI)
print(linearni_model)
predikce_linearniho_modelu = linearni_model.slope *  H + linearni_model.intercept
plt.figure()
plt.scatter(H, PI)
plt.scatter(H, predikce_linearniho_modelu)
plt.title("Predikce lineárního modelu")
plt.grid()

relativni_chyba = (PI - predikce_linearniho_modelu) / PI
plt.figure()
plt.scatter(H, relativni_chyba)

# výpočet residuí lineárního modelu
residua_linearni_model = PI - predikce_linearniho_modelu
plt.figure()
plt.scatter(H, residua_linearni_model)

print(stats.normaltest(residua_linearni_model))

# QQ plot
fig = plt.figure()
ax = fig.add_subplot(111)
stats.probplot(residua_linearni_model, dist="norm", plot=pylab)

def exponencialni_model_2parametry(x, w0, w1):
    """Dvouparametrovy exponcialni model h(x) = w0 * e^(w1 * x)"""
    return w0 * np.exp(w1 * x)
w0_odhad = np.linspace(0, 100, 100)  # počáteční odhady parametry w0 od 0 do 100 (100 hodnot)
w1_odhad = np.linspace(-1, 0, 100)  # počáteční odhady parametru w1
nejlepsi_soucet = 10 ** 50  # definicine nejlepšího součtu jako velké číslo (hledáme minimum)
nejlepsi_parametry_exp2 = (0, 0)
for w0_pocatecni in w0_odhad:  # iterjeme přes všechny počáteční odhady w0
    for w1_pocatecni in w1_odhad:
        # optimalizace
        parametry_exp2, _, infodict, _ , _  = optimize.curve_fit(
            exponencialni_model_2parametry, H, PI, full_output=True, p0=[w0_pocatecni, w1_pocatecni])
        # aktuální součet residuí
        aktualni_soucet = np.sum(np.abs(infodict["fvec"]))
        if aktualni_soucet < nejlepsi_soucet:
            # když najdeme lepší řešení, tak si uložíme parametry modelu
            nejlepsi_parametry_exp2 = parametry_exp2
print(parametry_exp2)

predikce_exp2_modelu = nejlepsi_parametry_exp2[0] * np.exp(nejlepsi_parametry_exp2[1] * H)
plt.figure()
plt.scatter(H, PI)
plt.scatter(H, predikce_exp2_modelu)
plt.show()