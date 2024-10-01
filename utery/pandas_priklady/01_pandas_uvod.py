import pandas as pd

# Definice obsahu tabulky po jednotlivých řádcích
data = [["Jakub", "Novák", 20],
        ["Karel", "Procházka", 20],
        ["Jan", "Novotný", 18]]

# Názvy jednotlivých sloupců
nazvy_sloupcu = ["Jmeno", "Prijmeni", "Vek"]

# Generování tabulky
df = pd.DataFrame(data=data, columns=nazvy_sloupcu)
# print(df, end="\n\n")

# Generování pomocí slovníku
data = {"Jmeno": ["Jakub", "Karel", "Jan"],
        "Prijmeni": ["Novák", "Procházka", "Novotný"],
        "Vek": [20, 20, 18]}
df2 = pd.DataFrame(data)
# print(df2)

# Funkce head a tail - prvních n a posledních n řádků tabulky
print(df.head(2)) # Zobrazuji první dva řádky tabulky
print("")
print(df2.tail(2))

# Funkce info - popisuje datové typy jednotlivých sloupců
print(df2.info())

# Funkce describe - statistiscký přehled o číselných hodnotách
print(df2.describe())

# Modus, medián
print(df2.Vek.mode())
print(df2["Vek"].median())

# Výběr části tabulky
print(df2[["Jmeno", "Prijmeni"]]) # Vrací dva sloupce Jméno a Příjmení
print(df2.loc[:, ["Jmeno", "Prijmeni"]]) # Vrací dva sloupec (pomocí loc)
print(df2.loc[0:1, :]) # Vrací dva řádky přes všechny sloupce
print(df2.loc[0, "Prijmeni"]) # Příjmení prvního člověka v tabulce
# Pomocí iloc
print(df2.iloc[:, 0:2]) # Vrací první dva sloupce
print(df2.iloc[0:2, :]) # Vrací první dva řádky
print(df2.iloc[1, 2]) # Věk druhého člověka v tabulce

# Změna řádkových indexů tabulky
seznam_indexu = [5, 10, 15]
df2.index = seznam_indexu
print("")
print(df2)
# Vypsani prvnich dvou radku
print("")
print(df2.loc[[5, 10], :])
print("")
print(df2.iloc[0:2, :])

# Přidání řádku tabulky pomocí lokátoru
novy_radek = ["Radka", "Dvorakova", 25]
df2.loc[20, :] = novy_radek
print("")
print(df2.shape) # Parametr shape vrací dimenze tabulky
# Přiřazení sloupečku tabulky pomocí indexu
df2["Zamestnani"] = None
print(df2.shape)
print(df2)
nova_zamestnani = ["celník", "policista", "lektor", "kuchařka"]
df2["Zamestnani"] = nova_zamestnani
print(df2)

# Odstranění řádků
print("Tabulka s odstraněným řádkem...")
print(df2.drop(15))
print("Původní tabulka je nezměněná")
print(df2)
df2.drop(15, inplace=True)
print("Změněná původní tabulka")
print(df2)

# Odstranění sloupce
print(df2.drop("Vek", axis=1))

# Spojení dvou tabulek se stejnými sloupci
df3 = df2.copy() # Vytvoření kopie tabulky
print("Sloučené tabulky")
print(pd.concat([df2, df3]))

# Spojení tabulek podle identifikátoru
data_jmena_veky = {"Jmeno": ["Karel", "Jan", "Pavel"],
                   "Vek": [20, 25, 30]}
data_zamestnani = {"Zamestnani": ["učitel", "právník", "výrobce bublifuků"]}
id = ["ID001", "ID002", "ID003"]  # identifikátory jednotlivých prvků tabulek
data_jmena_veky["id"] = id
data_zamestnani["id"] = id

df_jmena = pd.DataFrame(data_jmena_veky)
df_zamestnani = pd.DataFrame(data_zamestnani)

# Sloučení obou tabulek podle stejného názvu sloupců
print(df_jmena.merge(df_zamestnani, on="id")) # v případě stejného názvu dvou sloupců
df_jmena.rename(columns={"id": "ID"}, inplace=True) # přejmenování názvu sloupce
# Sloučení podle sloupců se dvěma různými názvy
print("")
print(df_jmena.merge(df_zamestnani, left_on="ID", right_on="id", how="left"))

# Přidání jednoho dalšího identifikátoru do tabulky se zaměstnáními
df_zamestnani.loc[df_zamestnani.shape[0], :] = ["celník", "ID004"]
print("")
print(df_jmena)
print(df_zamestnani)

print("LEFT JOIN")
print(df_jmena.merge(df_zamestnani, left_on="ID", right_on="id", how="left"))

