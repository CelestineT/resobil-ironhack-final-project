"""
extract_scraping.py
Scraping de données agricoles du Cameroun depuis IndexMundi.
Source : https://www.indexmundi.com/cameroon/
IndexMundi agrège les données officielles FAO, Banque Mondiale et CIA World Factbook.
Compétence C1 : extraction depuis une page web (scraping).
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

PAGES = [
    {
        "url": "https://www.indexmundi.com/cameroon/economy_profile.html",
        "topic": "economy"
    },
    {
        "url": "https://www.indexmundi.com/cameroon/land_use.html",
        "topic": "land_use"
    },
    {
        "url": "https://www.indexmundi.com/cameroon/labor_force_by_occupation.html",
        "topic": "labor_agriculture"
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def scrape_page(url, topic):
    logger.info("Scraping : %s", url)
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = []
    scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    tables = soup.find_all("table")
    for table in tables:
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if len(cells) >= 2:
                rows.append({
                    "topic": topic,
                    "label": cells[0],
                    "value": cells[1],
                    "extra": cells[2] if len(cells) > 2 else "",
                    "source_url": url,
                    "scraped_at": scraped_at,
                    "data_source": "IndexMundi (FAO / World Bank / CIA World Factbook)"
                })

    paragraphs = soup.find_all("p")
    for p in paragraphs[:5]:
        text = p.get_text(strip=True)
        if len(text) > 50:
            rows.append({
                "topic": topic,
                "label": "description",
                "value": text[:400],
                "extra": "",
                "source_url": url,
                "scraped_at": scraped_at,
                "data_source": "IndexMundi (FAO / World Bank / CIA World Factbook)"
            })

    logger.info("  -> %d lignes extraites pour '%s'", len(rows), topic)
    return rows

def main():
    os.makedirs("data/raw", exist_ok=True)
    all_rows = []

    for page in PAGES:
        try:
            rows = scrape_page(page["url"], page["topic"])
            all_rows.extend(rows)
        except Exception as e:
            logger.warning("Erreur pour %s : %s", page["url"], e)

    if not all_rows:
        logger.error("Aucune donnee extraite.")
        return

    df = pd.DataFrame(all_rows)
    out = f"data/raw/scraping_indexmundi_{datetime.now():%Y%m%d}.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    logger.info("Export termine : %s (%d lignes)", out, len(df))
    print("\n--- Apercu des donnees scrapees ---")
    print(df[["topic", "label", "value"]].head(15).to_string())

if __name__ == "__main__":
    main()