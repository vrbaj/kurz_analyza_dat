"""
Ukázka kontejnerových proměnných.
"""
# seznam - uspořádaná posloupnost, kterou lze měnit
seznam = [6, "řetězec", 6.5, [2, 3]]  # seznam
print(seznam)
# výběr prvku
print(seznam[0])
seznam[0] = 7  # nastavení hodnoty prvku v seznamu
print(seznam)
print(seznam[1:3])  # výběr vícero prvků
seznam[1:3] = ["řetězec2", 7.5]  # nastavení hodnot vícero
print(seznam)
print(len(seznam))  # počet prvků v seznamu
print(seznam[-2:])  # výběr posledních dvou prvků
seznam.append(100)  # přidání prvku do seznamu nakonec
print(seznam)
seznam.insert(1, "řetězec1")  # vkládání na konkrétní pozici v seznamu
print(seznam)
seznam.pop(1)  # smazání prvku ze seznamu
print(seznam)
seznam.append(7)  # přidání prvku nakonec
print(seznam)
seznam.remove(7)  # odstranění prvního prvku s číselnou hodnotou 7
print(seznam)

ciselny_seznam = [3, 1, 2]
ciselny_seznam.sort(reverse=True)  # setřídění prvků podle velikost
print(ciselny_seznam)
ciselny_seznam.reverse()  # obrácení pořadí prvků
print(ciselny_seznam)
seznam.reverse()
print(seznam)
print(ciselny_seznam + seznam)  # spojování seznamů
ciselny_seznam.append(2)  # přidání prvku nakonec
print(ciselny_seznam)
print(ciselny_seznam.count(2))  # spočítání prvků s konkrétní hodnotou
print(seznam.index(7.5))  # zjištění indexu hodnoty (první výskyt)
seznam.clear()  # smazání všech prvků seznamu
print(seznam)

"""
Komentář na několik
řádek
"""
# n-tice, tuple - uspořádaná sekvence neměných hodnot
muj_tuple = ("auto", "autobus", "vlak")
print(muj_tuple)
print(muj_tuple[0])  # výběr prvku na první pozici
dopravni_prostredek1, dopravni_prostredek2, dopravni_prostredek3 = muj_tuple
print(dopravni_prostredek1)
print(muj_tuple + (123,))  # připojení tuplů
print(muj_tuple.index("autobus"))  # vrácení prvního výskytu hodnoty v tuplu
print(muj_tuple.count("autobus"))  # zjištění počtu výskytů

# množina
mnozina = {1, 2, 3}  # obsahuje unikátní hodnoty, neměnitelná a neuspořádáná
print(mnozina)
print(3 in mnozina)  # vyskytuje se konkrétní hodnota? klíčové slovo in
mnozina.add(4)  # přidání prvku do množiny
print(mnozina)
mnozina.remove(1)
print(mnozina)
print(mnozina.union({2, 6}))  # sjednocení
print(mnozina.intersection({1, 2, 3}))  # průnik

muj_seznam = ["firma 1", "firma 2", "firma 3", "firma 1", "firma 1"]
print(len(muj_seznam))
seznam_unikatnich_hodnot = list(set(muj_seznam)) # seznam unikátních hodnot
print(seznam_unikatnich_hodnot)
tuple_unikatnich_hodnot = tuple(set(muj_seznam))
print(tuple_unikatnich_hodnot)

# slovník
slovnik = {"jmeno": "Honza",
           "vek": 39}
print(slovnik)
print(slovnik["jmeno"])  # přístup k hodnotě
print(slovnik.keys())  # seznam klíčových slov
print(slovnik.values())  # seznam hodnot
slovnik["jmeno"] = "Jan"  # změna hodnoty
print(slovnik)
slovnik["bydliste"] = "Praha"  # přidání nového klíče do slovníku a nastavení hodnoty
print(slovnik)
slovnik.pop("bydliste")  # smazání klíče
print(slovnik)
