
import pyodbc
import pandas as pd

DB = False

if DB:
    # definice připojení k DB
    CONN_STR = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=(localdb)\MSSQLLocalDB;"
        "DATABASE=MD2_VSCHT;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=no;"
    )
    # vytvoření připojení
    conn = pyodbc.connect(CONN_STR)
    # požadovaná SQL query
    query = """
    SELECT d.axisx, d.axisy, a.AuditAction, d.isCrimact
    FROM inetuser.MDx_Disorder d
    LEFT JOIN inetuser.MDx_AuditAction a ON d.cAuditAction = a.cAuditAction"""
    # načtení dat z db
    lokace = pd.read_sql(query, conn)
    # uložení do CSV
    lokace.to_csv("lokace.csv")
else:
    lokace = pd.read_csv("lokace.csv")
