"""
extract_resobil.py
-------------------
Script d'extraction des données RESOBIL depuis Azure Database for MySQL.

Compétence RNCP visée : C1 (Concevoir et développer un pipeline d'extraction
de données structurées en respectant les normes de qualité et de sécurité).

Usage :
    python extract_resobil.py --tables antenne membre projet --output ./data/raw

Variables d'environnement requises (voir .env.example) :
    AZURE_MYSQL_HOST
    AZURE_MYSQL_PORT
    AZURE_MYSQL_USER
    AZURE_MYSQL_PASSWORD
    AZURE_MYSQL_DATABASE
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(f"logs/extract_{datetime.now():%Y%m%d}.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

DEFAULT_TABLES = [
    "antenne",
    "membre",
    "membre_antenne",
    "coordinatrice",
    "activite_antenne",
    "activite_mensuelle",
    "evenement_collectif",
    "formation",
    "membre_formation",
    "projet",
    "production_agricole",
    "production_animale",
    "suivi_production_agricole",
    "commerce_antenne",
    "satisfaction_membre",
    "impact_social",
    "versement",
    "besoin_formations_digitale",
]


def get_connection():
    """Ouvre une connexion sécurisée à Azure Database for MySQL (TLS)."""
    try:
        conn = mysql.connector.connect(
            host=os.environ["AZURE_MYSQL_HOST"],
            port=int(os.environ.get("AZURE_MYSQL_PORT", 3306)),
            user=os.environ["AZURE_MYSQL_USER"],
            password=os.environ["AZURE_MYSQL_PASSWORD"],
            database=os.environ["AZURE_MYSQL_DATABASE"],
            ssl_disabled=False,  # Azure MySQL exige TLS
        )
        logger.info("Connexion Azure MySQL établie avec succès.")
        return conn
    except mysql.connector.Error as err:
        logger.error("Échec de connexion à Azure MySQL : %s", err)
        raise


def extract_table(conn, table_name: str) -> pd.DataFrame:
    """Extrait une table entière sous forme de DataFrame pandas."""
    query = f"SELECT * FROM `{table_name}`"
    logger.info("Extraction de la table %s", table_name)
    df = pd.read_sql(query, conn)
    logger.info("Table %s : %d lignes, %d colonnes", table_name, len(df), len(df.columns))
    return df


def anonymize_pii(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Masque les champs à caractère personnel avant export, conformément
    au registre RGPD (voir docs/rgpd_register.md).
    """
    pii_columns = [
        "telephone", "telephone_principal", "telephone_whatsapp",
        "email", "nom", "prenom", "village_de_residence",
    ]
    df = df.copy()
    for col in df.columns:
        if col in pii_columns:
            df[col] = df[col].apply(lambda x: "***MASKED***" if pd.notna(x) else x)
    return df


def save_extract(df: pd.DataFrame, table_name: str, output_dir: Path, anonymized: bool = False):
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_anonymized" if anonymized else ""
    out_path = output_dir / f"{table_name}{suffix}_{datetime.now():%Y%m%d}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    logger.info("Export écrit : %s", out_path)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Extraction des données RESOBIL (Azure MySQL).")
    parser.add_argument("--tables", nargs="+", default=DEFAULT_TABLES, help="Liste des tables à extraire")
    parser.add_argument("--output", default="./data/raw", help="Répertoire de sortie")
    parser.add_argument("--anonymize", action="store_true", help="Masquer les données personnelles (RGPD)")
    args = parser.parse_args()

    Path("logs").mkdir(exist_ok=True)
    output_dir = Path(args.output)

    conn = get_connection()
    try:
        for table in args.tables:
            try:
                df = extract_table(conn, table)
                if args.anonymize:
                    df = anonymize_pii(df, table)
                save_extract(df, table, output_dir, anonymized=args.anonymize)
            except mysql.connector.Error as err:
                logger.warning("Table %s ignorée (erreur : %s)", table, err)
                continue
    finally:
        conn.close()
        logger.info("Connexion fermée. Extraction terminée.")


if __name__ == "__main__":
    main()
