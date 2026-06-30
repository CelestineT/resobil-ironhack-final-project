"""
export_bigquery.py
--------------------
Exporte les extraits CSV RESOBIL (data/raw) vers Google BigQuery.

Compétence RNCP visée : C1/C2 (alimenter un entrepôt de données cloud).

Prérequis :
    - Un projet GCP avec BigQuery activé
    - Une clé de service JSON (GOOGLE_APPLICATION_CREDENTIALS dans .env)
    - pip install pandas-gbq google-cloud-bigquery

Usage :
    python export_bigquery.py --input ./data/raw --dataset resobil_dataset
"""

import argparse
import logging
import os
from pathlib import Path

import pandas as pd
import pandas_gbq
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def ensure_dataset(client: bigquery.Client, dataset_id: str, location: str = "EU"):
    dataset_ref = bigquery.DatasetReference(client.project, dataset_id)
    try:
        client.get_dataset(dataset_ref)
        logger.info("Dataset %s déjà existant.", dataset_id)
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        client.create_dataset(dataset)
        logger.info("Dataset %s créé (région %s).", dataset_id, location)


def export_csv_to_bigquery(csv_path: Path, project_id: str, dataset_id: str):
    table_name = csv_path.stem.split("_2")[0]  # retire le suffixe date si présent
    table_id = f"{dataset_id}.{table_name}"

    df = pd.read_csv(csv_path)
    logger.info("Chargement de %s (%d lignes) vers %s", csv_path.name, len(df), table_id)

    pandas_gbq.to_gbq(
        df,
        destination_table=table_id,
        project_id=project_id,
        if_exists="replace",
    )
    logger.info("Export terminé pour %s", table_id)


def main():
    parser = argparse.ArgumentParser(description="Export des extraits RESOBIL vers BigQuery.")
    parser.add_argument("--input", default="./data/raw", help="Répertoire des CSV à exporter")
    parser.add_argument("--dataset", default=os.environ.get("BIGQUERY_DATASET", "resobil_dataset"))
    parser.add_argument("--project", default=os.environ.get("BIGQUERY_PROJECT_ID"))
    args = parser.parse_args()

    if not args.project:
        raise SystemExit("BIGQUERY_PROJECT_ID manquant (voir .env.example)")

    client = bigquery.Client(project=args.project)
    ensure_dataset(client, args.dataset)

    input_dir = Path(args.input)
    csv_files = list(input_dir.glob("*.csv"))
    if not csv_files:
        logger.warning("Aucun fichier CSV trouvé dans %s", input_dir)
        return

    for csv_file in csv_files:
        export_csv_to_bigquery(csv_file, args.project, args.dataset)


if __name__ == "__main__":
    main()
