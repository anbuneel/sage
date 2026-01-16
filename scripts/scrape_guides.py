"""
Scrape Fannie Mae and Freddie Mac guide sections for SAGE MVP.
Extracts HomeReady and Home Possible eligibility content.

Requirements:
    pip install requests beautifulsoup4 lxml playwright
    playwright install chromium
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

# Try importing required packages
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"])
    import requests
    from bs4 import BeautifulSoup

# For Freddie Mac's JavaScript-heavy site
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Will attempt requests-based scraping first.")
    print("To install: pip install playwright && playwright install chromium")


# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
FANNIE_DIR = DATA_DIR / "fannie"
FREDDIE_DIR = DATA_DIR / "freddie"

# Create directories
FANNIE_DIR.mkdir(parents=True, exist_ok=True)
FREDDIE_DIR.mkdir(parents=True, exist_ok=True)


# URLs to scrape
FANNIE_MAE_URLS = {
    "B5-6_HomeReady_Overview": "https://selling-guide.fanniemae.com/sel/b5-6/homeready-mortgage",
    "B5-6-01_HomeReady_Eligibility": "https://selling-guide.fanniemae.com/sel/b5-6-01/homeready-mortgage-loan-and-borrower-eligibility",
    "B5-6-02_HomeReady_Underwriting": "https://selling-guide.fanniemae.com/sel/b5-6-02/homeready-mortgage-underwriting-methods-and-requirements",
    "B5-6-03_HomeReady_Pricing": "https://selling-guide.fanniemae.com/sel/b5-6-03/homeready-mortgage-loan-pricing-mortgage-insurance-and-special-feature-codes",
    "B3-5.1-01_Credit_Scores": "https://selling-guide.fanniemae.com/sel/b3-5.1-01/general-requirements-credit-scores",
    "B3-6-02_DTI_Ratios": "https://selling-guide.fanniemae.com/sel/b3-6-02/debt-income-ratios",
    "B2-1.2-01_LTV_Ratios": "https://selling-guide.fanniemae.com/sel/b2-1.2-01/loan-value-ltv-ratios",
}

FREDDIE_MAC_URLS = {
    "4501_Home_Possible_Overview": "https://guide.freddiemac.com/app/guide/chapter/4501",
    "4501.5_Home_Possible_Eligibility": "https://guide.freddiemac.com/app/guide/section/4501.5",
    "4501.9_Additional_Requirements": "https://guide.freddiemac.com/app/guide/section/4501.9",
    "5201_Credit_Assessment": "https://guide.freddiemac.com/app/guide/chapter/5201",
    "5401_Income_Assessment": "https://guide.freddiemac.com/app/guide/chapter/5401",
}

LENDER_LETTERS = {
    # Fannie Mae 2025
    "LL-2025-04_Loan_Limits_2026": "https://singlefamily.fanniemae.com/news-events/lender-letter-ll-2025-04-confirmation-conforming-loan-limit-values-2026",
    # Keep HomeReady enhancement as it's still in effect
    "LL-2024-01_HomeReady_Enhancement": "https://singlefamily.fanniemae.com/news-events/lender-letter-ll-2024-01-homeready-product-enhancement",
}

FREDDIE_BULLETINS = {
    "Bulletin_2025-16_Loan_Limits_2026": "https://guide.freddiemac.com/app/guide/bulletin/2025-16",
    "Bulletin_2025-9_Condo_Coop_Eligibility": "https://guide.freddiemac.com/app/guide/bulletin/2025-9",
    "Bulletin_2025-4_AMI_Limits_2025": "https://guide.freddiemac.com/app/guide/bulletin/2025-4",
}


def scrape_with_requests(url: str, name: str) -> str | None:
    """Scrape a URL using requests and BeautifulSoup."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"  Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Try to find main content area
        content = None

        # Fannie Mae specific selectors
        for selector in ["main", "article", ".content", "#content", ".guide-content", ".article-content"]:
            content = soup.select_one(selector)
            if content:
                break

        if not content:
            content = soup.body

        if content:
            # Get text with some structure preserved
            text = content.get_text(separator="\n", strip=True)
            # Clean up excessive newlines
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            return "\n\n".join(lines)

        return None

    except Exception as e:
        print(f"  Error fetching {name}: {e}")
        return None


def scrape_with_playwright(url: str, name: str) -> str | None:
    """Scrape a JavaScript-heavy page using Playwright."""
    if not PLAYWRIGHT_AVAILABLE:
        print(f"  Skipping {name} - Playwright not available")
        return None

    try:
        print(f"  Fetching with Playwright: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)

            # Wait for content to load
            time.sleep(2)

            # Get the page content
            content = page.content()
            browser.close()

            soup = BeautifulSoup(content, "lxml")

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Find main content
            main = soup.select_one("main") or soup.select_one(".content") or soup.body

            if main:
                text = main.get_text(separator="\n", strip=True)
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                return "\n\n".join(lines)

            return None

    except Exception as e:
        print(f"  Error with Playwright for {name}: {e}")
        return None


def save_content(content: str, filepath: Path, url: str):
    """Save scraped content to a file with metadata."""
    metadata = {
        "source_url": url,
        "scraped_at": datetime.now().isoformat(),
        "char_count": len(content),
    }

    # Save as text file with metadata header
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Source: {url}\n")
        f.write(f"# Scraped: {metadata['scraped_at']}\n")
        f.write(f"# Characters: {metadata['char_count']}\n")
        f.write("#" + "=" * 79 + "\n\n")
        f.write(content)

    print(f"  Saved: {filepath} ({metadata['char_count']:,} chars)")


def scrape_fannie_mae():
    """Scrape all Fannie Mae sections."""
    print("\n" + "=" * 60)
    print("SCRAPING FANNIE MAE SELLING GUIDE")
    print("=" * 60)

    for name, url in FANNIE_MAE_URLS.items():
        print(f"\n[{name}]")
        content = scrape_with_requests(url, name)

        if content and len(content) > 500:  # Minimum viable content
            filepath = FANNIE_DIR / f"{name}.txt"
            save_content(content, filepath, url)
        else:
            print(f"  Warning: Insufficient content for {name}")

        time.sleep(1)  # Be polite


def scrape_freddie_mac():
    """Scrape all Freddie Mac sections."""
    print("\n" + "=" * 60)
    print("SCRAPING FREDDIE MAC GUIDE")
    print("=" * 60)

    for name, url in FREDDIE_MAC_URLS.items():
        print(f"\n[{name}]")

        # Try requests first
        content = scrape_with_requests(url, name)

        # If requests fails or returns minimal content, try Playwright
        if not content or len(content) < 500:
            print("  Requests returned minimal content, trying Playwright...")
            content = scrape_with_playwright(url, name)

        if content and len(content) > 500:
            filepath = FREDDIE_DIR / f"{name}.txt"
            save_content(content, filepath, url)
        else:
            print(f"  Warning: Could not extract content for {name}")

        time.sleep(1)


def scrape_lender_letters():
    """Scrape Fannie Mae lender letters."""
    print("\n" + "=" * 60)
    print("SCRAPING FANNIE MAE LENDER LETTERS")
    print("=" * 60)

    letters_dir = FANNIE_DIR / "lender_letters"
    letters_dir.mkdir(exist_ok=True)

    for name, url in LENDER_LETTERS.items():
        print(f"\n[{name}]")
        content = scrape_with_requests(url, name)

        if content and len(content) > 200:
            filepath = letters_dir / f"{name}.txt"
            save_content(content, filepath, url)
        else:
            print(f"  Warning: Insufficient content for {name}")

        time.sleep(1)


def scrape_freddie_bulletins():
    """Scrape Freddie Mac guide bulletins."""
    print("\n" + "=" * 60)
    print("SCRAPING FREDDIE MAC BULLETINS")
    print("=" * 60)

    bulletins_dir = FREDDIE_DIR / "bulletins"
    bulletins_dir.mkdir(exist_ok=True)

    for name, url in FREDDIE_BULLETINS.items():
        print(f"\n[{name}]")

        # Try requests first
        content = scrape_with_requests(url, name)

        # If requests fails or returns minimal content, try Playwright
        if not content or len(content) < 500:
            print("  Requests returned minimal content, trying Playwright...")
            content = scrape_with_playwright(url, name)

        if content and len(content) > 200:
            filepath = bulletins_dir / f"{name}.txt"
            save_content(content, filepath, url)
        else:
            print(f"  Warning: Could not extract content for {name}")

        time.sleep(1)


def main():
    print("SAGE Guide Scraper")
    print("=" * 60)
    print(f"Data directory: {DATA_DIR}")
    print(f"Playwright available: {PLAYWRIGHT_AVAILABLE}")

    # Scrape all sources
    scrape_fannie_mae()
    scrape_freddie_mac()
    scrape_lender_letters()
    scrape_freddie_bulletins()

    # Summary
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)

    fannie_files = list(FANNIE_DIR.glob("*.txt"))
    freddie_files = list(FREDDIE_DIR.glob("*.txt"))
    letter_files = list((FANNIE_DIR / "lender_letters").glob("*.txt"))
    bulletin_files = list((FREDDIE_DIR / "bulletins").glob("*.txt"))

    print(f"\nFannie Mae sections: {len(fannie_files)}")
    print(f"Freddie Mac sections: {len(freddie_files)}")
    print(f"Fannie Mae Lender Letters: {len(letter_files)}")
    print(f"Freddie Mac Bulletins: {len(bulletin_files)}")

    if not PLAYWRIGHT_AVAILABLE and len(freddie_files) == 0:
        print("\n" + "-" * 60)
        print("NOTE: Freddie Mac scraping may require Playwright.")
        print("Install with: pip install playwright && playwright install chromium")
        print("-" * 60)


if __name__ == "__main__":
    main()
