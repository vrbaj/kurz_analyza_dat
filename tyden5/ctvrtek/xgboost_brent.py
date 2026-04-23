# definovanání použitých knihoven/modulů

import warnings
from dataclasses import dataclass
from typing import Tuple, List, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

# potlačení varování pomocí knihovny warnings
warnings.filterwarnings("ignore")

# nahrání dat z webu
SERIES: Dict[str,str] = {
    # denní cena ropy brent
    "brent": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU",
    # index dolaru
    "usd_index": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS",
    # index volatility
    "vix": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS",
    # index průmyslové produkce USA
    "indpro": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO",
}