# RESOBIL Data Pipeline — RNCP Bloc 1 (Développeur IA)

Pipeline de collecte, structuration et mise à disposition des données de la
coopérative RESOBIL (Réseau Oyili Bininga du Cameroun), hébergées sur
Azure Database for MySQL.

## Compétences RNCP couvertes

| Compétence | Livrable | Emplacement |
|---|---|---|
| C1 — Concevoir et développer un script d'extraction de données (multi-sources) | `extract_resobil.py`, `extract_meteo_api.py`, `extract_scraping.py`, `extract_fao_file.py` | `scripts/` |
| C2 — Modéliser les données (Merise) / requêtes d'analyse SQL | `merise_schema.md`, `sql_insights.sql` | `docs/`, `scripts/` |
| C5 — Développer une API pour exposer les données | `api.py` (Flask) | `api/` |
| Conformité RGPD | `rgpd_register.md` | `docs/` |
| Entreposage cloud (BigQuery) | `export_bigquery.py`, `retrieve_bigquery.py` | `scripts/` |

## Sources de données (C1 — mix de sources)

| # | Source | Contenu | Script | Type C1 |
|---|--------|---------|--------|---------|
| 1 | Azure MySQL | 24 tables RESOBIL (membres, finances, production, satisfaction, impact...) | `extract_resobil.py` | Base de données |
| 2 | Open Meteo API | Données météo pour les localités des antennes | `extract_meteo_api.py` | Service web (API) |
| 3 | IndexMundi (scraping) | Profil économique du Cameroun (PIB, commerce extérieur, agriculture...) | `extract_scraping.py` | Scraping web |
| 4 | FAO FAOSTAT (CSV) | Production agricole nationale du Cameroun, 1961-2024 | `extract_fao_file.py` | Fichier de données |
| 5 | Google BigQuery | Entrepôt analytique — requêtes cross-sources | `export_bigquery.py` / `retrieve_bigquery.py` | Système big data |

## Requêtes d'analyse SQL (C2)

10 requêtes d'insights métier sur la base `resobil_full`, documentées et
validées dans `scripts/sql_insights.sql` :

1. Top 10 antennes par membres actifs
2. Accès aux outils numériques parmi les membres (fracture digitale)
3. Production agricole totale par type de culture
4. Répartition des membres par niveau d'éducation
5. Vue financière par type de transaction
6. Besoin de micro-crédit exprimé par les membres
7. Vue synthétique de l'impact social multi-dimensionnel
8. Taux d'atteinte des objectifs par type d'événement collectif
9. Rentabilité de la production agricole par antenne
10. Pertes de récolte — volumes et causes principales

## Structure du dépôt

```
.
├── api/
│   └── api.py                    # API REST Flask (endpoints /antennes, /membres, /projets, ...)
├── scripts/
│   ├── extract_resobil.py        # Extraction Azure MySQL -> CSV (avec option --anonymize)
│   ├── extract_meteo_api.py      # Extraction météo via Open Meteo API
│   ├── extract_scraping.py       # Scraping du profil économique Cameroun (IndexMundi)
│   ├── extract_fao_file.py       # Extraction et nettoyage du fichier CSV FAOSTAT
│   ├── sql_insights.sql          # 10 requêtes SQL d'insights métier
│   ├── export_bigquery.py        # CSV -> BigQuery
│   └── retrieve_bigquery.py      # Lecture depuis BigQuery
├── docs/
│   ├── merise_schema.md          # MCD / MLD + règles de gestion
│   └── rgpd_register.md          # Registre des traitements (art. 30 RGPD)
├── data/
│   ├── raw/                      # Extraits CSV (non versionnés, .gitignore)
│   ├── external/                 # Fichiers de données externes (FAOSTAT, non versionnés)
│   └── results/                  # Résultats CSV des requêtes SQL
├── logs/                         # Logs d'exécution (non versionnés)
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseigner les identifiants Azure MySQL
```

## Utilisation

```bash
# Extraction complète (base de données)
python scripts/extract_resobil.py --output ./data/raw

# Extraction anonymisée (export externe / BigQuery)
python scripts/extract_resobil.py --output ./data/raw --anonymize

# Extraction météo (API)
python scripts/extract_meteo_api.py

# Extraction du profil économique du Cameroun (scraping)
python scripts/extract_scraping.py

# Extraction FAOSTAT (fichier de données)
python scripts/extract_fao_file.py

# Export vers BigQuery
python scripts/export_bigquery.py --input ./data/raw --dataset resobil_dataset

# Lancer l'API REST en local
python -m flask --app api/api.py run --debug
```

## Historique des versions (Git)

Voir `git log` — chaque évolution du pipeline (ajout d'une source de données,
correction d'un bug d'extraction, ajout d'un endpoint API) fait l'objet d'un
commit distinct, conformément aux bonnes pratiques de versioning attendues en C1.
