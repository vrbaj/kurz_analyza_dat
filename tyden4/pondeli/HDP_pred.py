import numpy as np
import pandas as pd
import requests
import json

from itertools import product
from tqdm import tqdm

from matplotlib import pyplot as plt
import seaborn as sns

# Stažení dat z ČSÚ o inflaci
base_url = "https://data.csu.gov.cz/api/dotaz/v1/data/vybery/"
kod_sady = "CEN0101CT02"
r = requests.get(base_url+kod_sady+"?format=JSON_STAT")