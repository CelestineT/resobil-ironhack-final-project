"""
extract_meteo_api.py
Extraction météo via Open Meteo API (gratuite, sans clé API).
Données pour les localités réelles des antennes RESOBIL.
Compétence C1 : extraction depuis un service web (API REST).
"""
import requests
import pandas as pd
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

ANTENNES_COORDS = [
    {"antenne": "OBALA",     "lat": 4.1667,  "lon": 11.5333},
    {"antenne": "SA'A",      "lat": 4.3667,  "lon": 11.6167},
    {"antenne": "OKOLA",     "lat": 3.9833,  "lon": 11.4167},
    {"antenne": "EBEBDA",    "lat": 4.6500,  "lon": 11.5167},
    {"antenne": "BATCHENGA", "lat": 4.2333,  "lon": 11.6667},
    {"antenne": "MBANDJOCK", "lat": 4.4500,  "lon": 11.9000},
    {"antenne": "MONATELE",  "lat": 4.1500,  "lon": 11.2000},
    {"antenne": "EVODOULA",  "lat": 3.9167,  "lon": 11.3000},
]

def fetch_meteo(lat, lon, antenne):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Africa/Douala",
        "past_days": 30
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()["daily"]
    df = pd.DataFrame(data)
    df["antenne"] = antenne
    logger.info("Meteo extraite pour %s : %d jours", antenne, len(df))
    return df

def main():
    os.makedirs("data/raw", exist_ok=True)
    all_dfs = []
    for a in ANTENNES_COORDS:
        try:
            df = fetch_meteo(a["lat"], a["lon"], a["antenne"])
            all_dfs.append(df)
        except Exception as e:
            logger.warning("Erreur pour %s : %s", a["antenne"], e)
    result = pd.concat(all_dfs, ignore_index=True)
    out = f"data/raw/meteo_api_{datetime.now():%Y%m%d}.csv"
    result.to_csv(out, index=False)
    logger.info("Export termine : %s (%d lignes)", out, len(result))
    print(result.head(10))

if __name__ == "__main__":
    main()