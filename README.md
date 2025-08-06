# USCIS Policy Manual Crawler

A Python script to crawl and extract content from the USCIS Policy Manual.

## Features

- Extracts content from USCIS Policy Manual chapters
- Organizes data by volume, section, and chapter
- Cleans and formats content
- Saves output in JSON format with metadata

## Requirements

- Python 3.x
- Chrome/Chromium browser
- Required Python packages:
  - selenium
  - beautifulsoup4
  - webdriver-manager

## Installation

1. Clone this repository:
```bash
git clone [your-repo-url]
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required packages:
```bash
pip install selenium beautifulsoup4 webdriver-manager
```

## Usage

Run the script:
```bash
python data.py
```

The script will:
1. Crawl the USCIS Policy Manual
2. Extract content from chapters
3. Save the data in a JSON file with timestamp

## Output Format

```json
{
  "metadata": {
    "name": "uscis_policy_manual",
    "version": "1.0.0",
    "description": "Scraped sample chapters from USCIS Policy Manual"
  },
  "data": [
    {
      "id": "uuid",
      "content": "chapter content",
      "metadata": {
        "volume": "Volume X",
        "chapter": "Chapter Title",
        "section": "Part Y",
        "reference_url": "url"
      }
    }
  ]
}
```
