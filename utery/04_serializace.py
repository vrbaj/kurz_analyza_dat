"""
Serializace - převod datové struktury v paměti do souboru
"""
import json
import pickle

seznam = [1, 2, 3]
with open("data.json", "w") as f:
    json.dump(seznam, f)

with open("data.json", "r") as f:
    nacteny_seznam = json.load(f)
print(nacteny_seznam)
print(type(nacteny_seznam))

with open("data.pickle", "wb") as f:
    pickle.dump(seznam, f)

with open("data.pickle", "rb") as f:
    nacteny_pickle = pickle.load(f)
print(nacteny_pickle)
print(type(nacteny_pickle))