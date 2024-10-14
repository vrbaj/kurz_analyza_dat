"""
Ukázka práce s řetězci
"""
jmeno = "Alex"
vek = 40

print(f"Jmenuji se {jmeno} a je mi {vek}.")
print(f"Jmenuji se {jmeno} a je mi {vek:b}.")  # binarní
print(f"Jmenuji se {jmeno} a je mi {40.35987:.2f}.")  # float

identita = ("John", "Doe", "III.")
print("---".join(identita)) # spojí v jeden řětězec pomocí předdefinovaného podřetězce

dlouhy_retezec = "Nejaka dlouha veta s hodne slovy."
print(dlouhy_retezec.split(" "))  # rozdělí řetězec na podřetězce
# replace - nahradí podřetězec
print(dlouhy_retezec.replace("hodne", "malo").replace("dlouha", "kratka"))

# nahrazení pouze prvních dvou výskytů
print("Ahoj ahoj ahoj ahoj ahoj ahoj".replace("ahoj", "neco", 2))

print("text".zfill(10))
print("-123".zfill(6))

# převedení na malé/velké znaky
retezec = "AbEc3Da"
print(retezec.lower())  # převod na malá písmena
print(retezec.upper())  # převod na velká písmena

data = "         jmeno firmy \n          "
data = data.replace("\n", "")
print(data)
print(data.strip(" "))  # odstranění znaků
print(data.rstrip(" "))
print(data.lstrip(" "))

firma = "firma, s.r.o."
firma = "Firma s r.o."
print(firma.replace(" ", "").replace(".", "").replace(",","").lower())

retez = "abeceda abeceda"
print(retez.find("da", 6, 9))  # první výskyt podřetězce

print(retez.count("ab"))
