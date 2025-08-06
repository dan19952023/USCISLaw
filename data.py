import uuid
import json
import logging
from datetime import datetime
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


def init_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def clean_content(text, filter_ui=True):
    lines = text.splitlines()
    filtered = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if filter_ui:
            if line.startswith("Breadcrumb") or line.startswith("Content navigation"):
                continue
            if line.lower() in {"guidance", "resources", "appendices", "updates"}:
                continue
        filtered.append(line)
    return "\n".join(filtered)


def extract_volume_section(url):
    try:
        path = urlparse(url).path
        parts = path.split("/")[-1].split("-")
        volume = f"Volume {parts[1]}" if len(parts) > 1 else "Unknown Volume"
        section = f"Part {parts[3].upper()}" if len(parts) > 3 else "Unknown Section"
        return volume, section
    except Exception:
        return "Unknown Volume", "Unknown Section"


def extract_chapter_content(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "content")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        content_div = soup.find("div", id="content")
        if content_div:
            return clean_content(content_div.get_text(separator="\n", strip=True))
        else:
            logging.warning(f"No content found in {url}")
    except Exception as e:
        logging.error(f"Error extracting {url}: {e}")
    return ""


def crawl_sample_chapters(limit=3):
    base_url = "https://www.uscis.gov/policy-manual/table-of-contents"
    driver = init_driver(headless=True)
    data = []

    try:
        logging.info(f"Loading TOC: {base_url}")
        driver.get(base_url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        toc_tree = soup.find("div", class_="toc-tree")
        if not toc_tree:
            logging.error("TOC not found.")
            return []

        count = 0
        for a in toc_tree.find_all("a", href=True):
            if count >= limit:
                break
            href = a["href"]
            title = a.get_text(strip=True)
            if not href.startswith("/policy-manual/"):
                continue

            full_url = "https://www.uscis.gov" + href
            logging.info(f"Fetching: {title} - {full_url}")
            content = extract_chapter_content(driver, full_url)
            volume, section = extract_volume_section(full_url)

            data.append({
                "id": str(uuid.uuid4()),
                "content": content,
                "metadata": {
                    "volume": volume,
                    "chapter": title,
                    "section": section,
                    "reference_url": full_url
                }
            })
            count += 1

    finally:
        driver.quit()

    return data


def main():
    data = crawl_sample_chapters(limit=2)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = {
        "metadata": {
            "name": "uscis_policy_manual",
            "version": "1.0.0",
            "description": "Scraped sample chapters from USCIS Policy Manual"
        },
        "data": data
    }

    output_file = f"uscis_sample_output_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logging.info(f"Saved {len(data)} records to {output_file}")


if __name__ == "__main__":
    main()
