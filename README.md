# RESOBIL Data Pipeline — RNCP Bloc 1 (Développeur IA)

Pipeline de collecte, structuration et mise à disposition des données de la
coopérative RESOBIL (Réseau Oyili Bininga du Cameroun), hébergées sur
Azure Database for MySQL.

## Compétences RNCP couvertes

| Compétence | Livrable | Emplacement |
|---|---|---|
| C1 — Concevoir et développer un script d'extraction de données | `extract_resobil.py` | `scripts/` |
| C2 — Modéliser les données (Merise) | `merise_schema.md` | `docs/` |
| C5 — Développer une API pour exposer les données | `api.py` (Flask) | `api/` |
| Conformité RGPD | `rgpd_register.md` | `docs/` |
| Entreposage cloud (BigQuery) | `export_bigquery.py` | `scripts/` |

## Structure du dépôt

```
.
├── api/
│   └── api.py                # API REST Flask (endpoints /antennes, /membres, /projets, ...)
├── scripts/
│   ├── extract_resobil.py    # Extraction Azure MySQL -> CSV (avec option --anonymize)
│   └── export_bigquery.py    # CSV -> BigQuery
├── docs/
│   ├── merise_schema.md      # MCD / MLD + règles de gestion
│   └── rgpd_register.md      # Registre des traitements (art. 30 RGPD)
├── data/raw/                 # Extraits CSV (non versionnés, .gitignore)
├── logs/                     # Logs d'exécution (non versionnés)
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
# Extraction complète
python scripts/extract_resobil.py --output ./data/raw

# Extraction anonymisée (export externe / BigQuery)
python scripts/extract_resobil.py --output ./data/raw --anonymize

# Export vers BigQuery
python scripts/export_bigquery.py --input ./data/raw --dataset resobil_dataset

# Lancer l'API REST en local
flask --app api/api run --debug
```

## Historique des versions (Git)

Voir `git log` — chaque évolution du pipeline (ajout d'une table, correction
d'un bug d'extraction, ajout d'un endpoint API) fait l'objet d'un commit
distinct, conformément aux bonnes pratiques de versioning attendues en C1.
