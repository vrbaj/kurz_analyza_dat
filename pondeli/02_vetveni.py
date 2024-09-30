a = 6
b = 5
c = 7
# logické výrazy
print(a == b)  # test rovnosti
print(a != b)  # test nerovnosti
print(a > b)  # a je větší než b
print(a < b)
print(a <= b)  # a je menší nebo rovno b
print(a >= b)  # a je větší nebo rovno b
# operátory OR a AND
print(a > b and c > a)  # logické A
print(a < b or c > a)  # logické NEBO
print(not a > b) # negace (doplněk)

# větvení programu
nejaky_text = "A"
nejake_cislo = 11
if nejaky_text == "A":  # test zda nejaky_text je roven "A"
    print("udělej A")
    print("udělej A ještě jednou")
    if nejake_cislo == 10:  # test zda je nejake_cislo rovno 10
        print("dělám A a nějaké číslo je 10")
    else:
        print("dělám A a nějaké číslo není 10")
elif nejaky_text == "B":
    print("udělej B")
else:
    print("udělej něco jiného")

if nejake_cislo > 15:
    pass  # minimální implementace bloku, která nic nedělá
