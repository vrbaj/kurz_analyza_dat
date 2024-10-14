with open("soubor.txt", encoding="utf8") as f:
    obsah_souboru = f.read()

print(obsah_souboru)
print("-------------------------")

with open("soubor.txt", encoding="utf8") as f:
    deset_znaku = f.read(10)  # počet znaků
print(deset_znaku)
print("------------------------")
with open("soubor.txt", encoding="utf8") as f:
    print(f.readline())
    print(f.readline())

print("--------------------------")
with open("soubor.txt", encoding="utf8") as f:
    for radek in f:
        print(radek)

print("--------------------------")
with open("soubor.txt", encoding="utf8") as f:
    vsechny_radky = f.readlines()
    print(vsechny_radky)

print("--------------------------")
with open("soubor_pro_psani.txt", "w", encoding="utf8") as f:
    f.write("Řádek 1\n")

with open("soubor_pro_psani.txt", "a", encoding="utf8") as f:
    f.write("Řádek 2\n")

with open("soubor_pro_psani.txt", "a", encoding="utf8") as f:
    seznam_radek = ["Řádek 3\n", "Řádek 4\n"]
    f.writelines(seznam_radek)