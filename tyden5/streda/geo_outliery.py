
import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=(localdb)\MSSQLLocalDB;"
    "DATABASE=MD2_VSCHT;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=no;"
)

conn = pyodbc.connect(CONN_STR)
print(conn)
