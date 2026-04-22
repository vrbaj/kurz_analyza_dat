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

# připojení k DB
conn = pyodbc.connect(conn_string)

# vytvoření pd DataFrame s výsledkem query
df = pd.read_sql(query, conn)

# odpojení od db
conn.close()

# kontrola výsledku query
print(df.head())
print(df.shape)
print(df.columns)