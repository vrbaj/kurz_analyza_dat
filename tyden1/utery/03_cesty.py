from pathlib import Path
import shutil


if __name__ == "__main__":
    cesta = Path("")
    print(cesta.resolve())  # vrátí absolutní cestu
    cela_cesta = Path("C:/", "Users")
    print(cela_cesta.resolve())
    # cela_cesta = Path("/", "home", "user")
    for adresare in cesta.iterdir():  # iterace přes podadresáře
        print(adresare)
    print("-----------------")
    for vyhovujici in cesta.glob("0*"):  # nalezení všeho co začíná znakem 0
        print(vyhovujici)

    for podsoubor in cesta.glob("**/*"):  # nalezení všech souborů a podadresářů
        print(podsoubor)

    print("-------------------")
    for textak in cesta.glob("**/*.txt"):  # nalezení všech txt souborů v adresáři a podadresářích
        print(textak)

    adresare = Path("./temp", "temp2")
    adresare.mkdir(exist_ok=True, parents=True)  # vytvoření adresářů

    # Path(".", "temp").rename("prejmenovany_temp")  # přejmenování adresáře/souboru
    zdroj = Path("", "soubory", "soubor.txt")
    cil = Path("", "prejmenovany_temp", "soubor_kopie.txt")
    # shutil.copy2(zdroj, cil)  # kopírování souboru
    # zdroj.rename(cil)  # přesun souboru

    adresar_pro_smazani = Path("", "temp")
    print(adresar_pro_smazani.resolve())
    shutil.rmtree(adresar_pro_smazani)

    soubor_pro_smazani = Path("", "soubory", "soubor_pro_psani.txt")
    soubor_pro_smazani.unlink(missing_ok=True)
