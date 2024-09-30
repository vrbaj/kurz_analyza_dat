"""
Smyčky - příklady a ukázky
"""
# while
iterace = 0
while iterace < 10:  # vykonává následující blok kódu dokud je splněná logická podmínka
    iterace = iterace + 1
    print(f"iterace - {iterace}")  # ukázka f-string. za {iterace} se dosadí hodnota proměnné

# ukazka odstraneni vsech prvku ze seznamu
muj_seznam = [7, 7, 7, 7, 5, 7, 7, 1]
while 7 in muj_seznam:  # je v muj_seznam prvek 7?
    muj_seznam.remove(7)  # odstraň z muj_seznam prvek s hodnotou 7
print(muj_seznam)  # vytiskni muj_seznam

# předčasné ukončení smyčky
iterace = 0
while iterace < 10:
    iterace = iterace + 1
    if iterace == 4:
        break
    print(f"iterace - {iterace}")
# continue
iterace = 0
while iterace < 10:
    iterace = iterace + 1
    if iterace % 2 == 0:
        continue  # okamžité ukončení iterace a spuštění další
    print(f"iterace - {iterace}")

# for smyčka - umožní iterovat přes iterovatelný objekt
for pismeno in "abeceda":
    print(pismeno)

for polozka_seznamu in [1, "slovo", [2.5, 7]]:
    print(polozka_seznamu)

for polozka_tuplu in (1, 2, 3):
    print(polozka_tuplu)

slovnik = {"barva": "modra", "typ_auta": "volvo"}
for klic in slovnik:
    print(klic, slovnik[klic])

# items - vrací dvojici klíč + hodnota slovníku
for klic, hodnota in slovnik.items():
    if klic == "barva":
        break  # okamžité ukončení for smyčky
    print(f"{klic} - {hodnota}")

for klic, hodnota in slovnik.items():
    if klic == "barva":
        continue  # okamžité ukončení aktuální iterace for smyčky
    print(f"{klic} - {hodnota}")

for y in range(1, 10):
    for x in range(2, 14, 3):
        if x == 5:
            print(x)