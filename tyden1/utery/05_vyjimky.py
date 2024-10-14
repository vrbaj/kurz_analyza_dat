x = 3
y = 2
try:
    print(x / y)
except TypeError as ex:
    print(ex)
    print(int(x) / int(y))
except ZeroDivisionError as ex:
    print("Dělím nulou")
    print(x / (y + 0.000000001))
except Exception as ex:
    print(ex)
else:
    print("Vše proběhlo v pořádku")
finally:
    del x
    del y
    print("finally proběhnul")