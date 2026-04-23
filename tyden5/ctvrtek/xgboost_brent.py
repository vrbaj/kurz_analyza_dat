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