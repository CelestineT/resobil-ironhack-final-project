import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv("AZURE_MYSQL_HOST"),
        port=int(os.getenv("AZURE_MYSQL_PORT")),
        user="admin_resobil",
        password=os.getenv("AZURE_MYSQL_PASSWORD"),
        database=os.getenv("AZURE_MYSQL_DATABASE")
    )

    print("Connexion réussie")
    conn.close()

except Exception as e:
    print("ECHEC CONNEXION")
    print(e)