import pandas as pd
from tqdm import tqdm

data_substring = ["kos", "pes", "kocka", "kralik", "kun"] * 10000000
data_string = "kos leta"

# TQDM ukazuje postup vypoctu v nejake smycce.
for substring in tqdm(data_substring):
    substring in data_string