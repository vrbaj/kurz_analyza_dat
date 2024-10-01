def nazev_funkce():
    """
    Tahle funkce tiskne řetězec.
    """
    print("Tohle je z funkce nazev_funkce()")

nazev_funkce()
nazev_funkce()
nazev_funkce()

def predstav_se(jmeno, prijmeni):
    """
    Funkce demonstrující použití argumentů.
    :param jmeno: jméno osoby (str)
    :param prijmeni: příjmení osoby
    :return: None
    """
    print(f"Jmenuji {jmeno} {prijmeni}")

predstav_se("Alexandr", "Novak")
predstav_se("Nikola", "Šuhaj")

def obvod_obdelniku(a, b):
    """Návratová hodnota z funkce"""
    return 2 * (a + b)

obvod = obvod_obdelniku(3, 7.5)
print(obvod)

def ziskej_extremy(seznam):
    """Dvě návratové hodnoty z funkce"""
    return min(seznam), max(seznam)

minimalni_hodnota, maximalni_hodnota = ziskej_extremy([3, 4, 6, 7, 8])
print(f"Minimum je {minimalni_hodnota}, maximum je {maximalni_hodnota}")  # formátovací řetězec

print(type(ziskej_extremy([1, 2, 3])))
test = ziskej_extremy([1, 2, 3])
print(test) # ukázka že defaultní návratový typ vícero hodnot je tuple

def test_slovnik(a, b):
    """
    Při větším počtu návratových hodnot je vhodné použít slovník (řeší problémy s pořadím
    návratových hodnot
    """
    return {"vysledek1": a, "vysledek2": b}

vysledek_slovnik = test_slovnik(1, 2)
print(vysledek_slovnik)

def nasobeni_rady(*args):
    """
    Libovolný počet argumentů.
    """
    celkovy_soucin = 1
    for argument in args:
        celkovy_soucin = celkovy_soucin * argument
    return celkovy_soucin

print(nasobeni_rady(1, 2, 3))

def ukazka_argumenty(povinny_argument, *args):
    print(f"Toto je {povinny_argument}")
    for argument in args:
        print(f"Toto je volitelný argument {argument}")

print(ukazka_argumenty(1, 2, 3))

def vytiskni_jmeno(jmeno, prijmeni):
    print(f"{jmeno} {prijmeni}")

vytiskni_jmeno(prijmeni="Turing", jmeno="Alan")

def vytiskni_latinskoamericke_jmeno(**kwargs):
    """
    Libovolný počet pojmenovaných argumentů
    """
    if "kmotrovske" in kwargs.keys():
        print(f"{kwargs['jmeno']} {kwargs['prostredni_jmeno']} {kwargs['prijmeni']} {kwargs['kmotrovske']}")
    else:
        print(f"{kwargs['jmeno']} {kwargs['prostredni_jmeno']} {kwargs['prijmeni']}")

vytiskni_latinskoamericke_jmeno(jmeno="Louis", prostredni_jmeno="Rodriquez", prijmeni="Lopez", kmotrovske = "Juan")

def oblibena_barva(barva="červená"):
    print(f"Moje oblíbená barva je {barva}")

oblibena_barva()
oblibena_barva("modrá")
oblibena_barva(barva="zelená")

seznam_hodnot = [1, 5.5, "3", 7, "8.5"]
print(list(map(float, seznam_hodnot)))  # funkce map aplikuje float na každou položku proměnné seznam_hodnot

print(type(map(float, seznam_hodnot)))  # pozor, výstupem funkce map je objekt třídy map, nikoliv seznam