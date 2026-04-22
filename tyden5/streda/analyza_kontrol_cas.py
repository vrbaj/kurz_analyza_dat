import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import csv
import os

from connection_string import conn_string

query = """
SELECT
    d.recdate,
    d.isCrimact,
    d.cAuditAction,
    d.RUIAN_KOD_OBEC,
    d.LocTime,
    d.LocDate,
    d.crecorda,
    o.divrep
FROM inetuser.MDx_Disorder d
JOIN inetuser.MDx_Order o ON d.crecorda = o.crecord;
"""