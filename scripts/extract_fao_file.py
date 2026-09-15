"""
extract_fao_file.py
Extraction et nettoyage du fichier CSV FAOSTAT (source : fichier de données externe).
Compétence C1 : extraction depuis un fichier de données.

Fichier source attendu : Production_Crops_Livestock_E_Africa_NOFLAG.csv
(ou Production_Crops_Livestock_E_Africa.csv si tu veux garder les colonnes de flags/notes)
téléchargé depuis https://www.fao.org/faostat/en/#data/QCL (bulk download "Africa").

Ce fichier couvre TOUTE l'Afrique, pas seulement le Cameroun : ce script filtre
sur le pays et remet le format "large" (une colonne par année, ex. Y1961, Y1962...)
en format "long" (une ligne par année) pour faciliter l'analyse et le chargement en base.
"""
import pandas as pd
import re
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

# Adapter le chemin selon le fichier réellement placé dans data/external/
INPUT_PATH = "data/external/Production_Crops_Livestock_E_Africa_NOFLAG.csv"
COUNTRY = "Cameroon"


def explore_items(input_path=INPUT_PATH, country=COUNTRY):
    """Étape 0 (optionnelle) : lister les Item/Element disponibles pour le pays choisi,
    pour vérifier les libellés exacts avant de filtrer (ex. 'Maize (corn)' et non 'Maize')."""
    logger.info("Exploration des libellés disponibles pour %s...", country)
    df = pd.read_csv(input_path, encoding="latin1", low_memory=False)
    df_country = df[df["Area"] == country]
    items = sorted(df_country["Item"].unique())
    elements = sorted(df_country["Element"].unique())
    logger.info("%d cultures/produits disponibles pour %s", len(items), country)
    logger.info("Elements disponibles : %s", elements)
    return items, elements


def extract_fao(input_path=INPUT_PATH, country=COUNTRY, items=None, elements=None):
    """Étape 1 : extraction, filtrage pays/cultures et passage wide -> long."""
    logger.info("Lecture du fichier FAO : %s", input_path)
    df = pd.read_csv(input_path, encoding="latin1", low_memory=False)
    logger.info("Fichier brut : %d lignes, %d colonnes", df.shape[0], df.shape[1])

    # 1. Filtrer sur le pays
    df_country = df[df["Area"] == country].copy()
    logger.info("Lignes après filtre Area == %s : %d", country, len(df_country))

    # 2. Filtrer sur les cultures/produits d'intérêt (optionnel)
    if items:
        df_country = df_country[df_country["Item"].isin(items)]
        logger.info("Lignes après filtre Item : %d", len(df_country))

    # 3. Filtrer sur le type d'indicateur (Production, Area harvested, Yield...)
    if elements:
        df_country = df_country[df_country["Element"].isin(elements)]
        logger.info("Lignes après filtre Element : %d", len(df_country))

    # 4. Identifier les colonnes années (Y1961, Y1962... en excluant les colonnes
    #    de flags 'Y1961F' et de notes 'Y1961N' si présentes dans la version non-NOFLAG)
    year_cols = [c for c in df_country.columns if re.fullmatch(r"Y\d{4}", c)]
    if not year_cols:
        raise ValueError("Aucune colonne année détectée — vérifier le format du fichier source.")
    logger.info("Colonnes années détectées : %s -> %s (%d années)", year_cols[0], year_cols[-1], len(year_cols))

    id_cols = [c for c in ["Area Code", "Area", "Item Code", "Item", "Element Code", "Element", "Unit"]
               if c in df_country.columns]

    # 5. Passage wide -> long
    df_long = df_country.melt(id_vars=id_cols, value_vars=year_cols,
                               var_name="year_col", value_name="value")
    df_long["year"] = df_long["year_col"].str.replace("Y", "", regex=False).astype(int)
    df_long = df_long.drop(columns="year_col").dropna(subset=["value"])
    logger.info("Lignes après melt et suppression des valeurs manquantes : %d", len(df_long))

    # 6. Nettoyage des noms de colonnes
    df_long.columns = [c.strip().lower().replace(" ", "_") for c in df_long.columns]

    # 7. Export
    os.makedirs("data/raw", exist_ok=True)
    out = f"data/raw/fao_{country.lower()}_{datetime.now():%Y%m%d}.csv"
    df_long.to_csv(out, index=False)
    logger.info("Export : %s (%d lignes nettoyées)", out, len(df_long))
    return df_long


if __name__ == "__main__":
    # Étape 0 (à lancer une première fois pour vérifier les libellés exacts) :
    # items, elements = explore_items()
    # print(items)

    df = extract_fao(
        items=["Maize (corn)", "Cassava, fresh", "Groundnuts, excluding shelled"],
        elements=["Production", "Area harvested", "Yield"],
    )
    print(df.head(10))