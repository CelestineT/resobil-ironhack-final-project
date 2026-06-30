"""
retrieve_bigquery.py
----------------------
Récupère des données depuis BigQuery (point 9 du livrable RNCP/Ironhack :
"Retrieve Data from BigQuery").

Ce script illustre BigQuery comme source "système big data", complémentaire
à la source "base de données relationnelle" (Azure MySQL) exigée par la
compétence C1 ("un mix entre au moins : service web, fichier, scraping,
base de données et système big data").

Usage :
    python retrieve_bigquery.py --dataset resobil_dataset --table antenne
    python retrieve_bigquery.py --dataset resobil_dataset --query "SELECT ..."
"""

import argparse
import logging
import os

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def get_client(project_id: str) -> bigquery.Client:
    return bigquery.Client(project=project_id)


def retrieve_table(client: bigquery.Client, dataset: str, table: str) -> pd.DataFrame:
    """Récupère une table entière depuis BigQuery sous forme de DataFrame."""
    table_id = f"{client.project}.{dataset}.{table}"
    query = f"SELECT * FROM `{table_id}`"
    logger.info("Exécution de la requête BigQuery : %s", query)
    df = client.query(query).to_dataframe()
    logger.info("Récupéré %d lignes / %d colonnes depuis %s", len(df), len(df.columns), table_id)
    return df


def retrieve_custom_query(client: bigquery.Client, sql: str) -> pd.DataFrame:
    """Exécute une requête SQL libre sur BigQuery (ex. agrégation cross-tables)."""
    logger.info("Exécution de la requête personnalisée BigQuery.")
    df = client.query(sql).to_dataframe()
    logger.info("Récupéré %d lignes / %d colonnes.", len(df), len(df.columns))
    return df


def main():
    parser = argparse.ArgumentParser(description="Récupération de données depuis BigQuery.")
    parser.add_argument("--project", default=os.environ.get("BIGQUERY_PROJECT_ID"))
    parser.add_argument("--dataset", default=os.environ.get("BIGQUERY_DATASET", "resobil_dataset"))
    parser.add_argument("--table", help="Nom de la table à récupérer intégralement")
    parser.add_argument("--query", help="Requête SQL personnalisée à exécuter")
    parser.add_argument("--output", default="./data/from_bigquery", help="Répertoire de sortie CSV")
    args = parser.parse_args()

    if not args.project:
        raise SystemExit("BIGQUERY_PROJECT_ID manquant (voir .env.example)")

    client = get_client(args.project)

    if args.query:
        df = retrieve_custom_query(client, args.query)
        out_name = "custom_query_result.csv"
    elif args.table:
        df = retrieve_table(client, args.dataset, args.table)
        out_name = f"{args.table}_from_bigquery.csv"
    else:
        raise SystemExit("Spécifier --table ou --query")

    os.makedirs(args.output, exist_ok=True)
    out_path = os.path.join(args.output, out_name)
    df.to_csv(out_path, index=False, encoding="utf-8")
    logger.info("Résultat sauvegardé : %s", out_path)
    print(df.head())


if __name__ == "__main__":
    main()
