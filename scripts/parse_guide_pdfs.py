#!/usr/bin/env python3
"""
Parse Fannie Mae and Freddie Mac guide PDFs into structured text files.

This script extracts text from the guide PDFs and saves them as structured
text files that can be embedded into Pinecone for RAG.

Usage:
    pip install pdfplumber
    python parse_guide_pdfs.py
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import pdfplumber
except ImportError:
    print("Please install pdfplumber: pip install pdfplumber")
    sys.exit(1)


# Default PDF paths (Windows user Downloads folder)
FANNIE_PDF = Path(os.path.expanduser("~/Downloads/Selling-Guide_12-10-25_Highlight.pdf"))
FREDDIE_PDF = Path(os.path.expanduser("~/Downloads/FreddieMac_TheGuide.pdf"))

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "guides_parsed"


def extract_pdf_info(pdf_path: Path) -> dict:
    """Extract basic info about a PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        return {
            "path": str(pdf_path),
            "pages": len(pdf.pages),
            "metadata": pdf.metadata,
        }


def extract_full_text(pdf_path: Path, max_pages: Optional[int] = None) -> str:
    """Extract all text from a PDF."""
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        pages_to_process = pdf.pages[:max_pages] if max_pages else pdf.pages
        total = len(pages_to_process)

        for i, page in enumerate(pages_to_process):
            if i % 50 == 0:
                print(f"  Processing page {i+1}/{total}...")

            text = page.extract_text()
            if text:
                text_parts.append(f"\n\n--- PAGE {i+1} ---\n\n{text}")

    return "\n".join(text_parts)


def extract_sample(pdf_path: Path, start_page: int = 0, num_pages: int = 10) -> str:
    """Extract a sample of pages from a PDF for analysis."""
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        end_page = min(start_page + num_pages, len(pdf.pages))

        for i in range(start_page, end_page):
            page = pdf.pages[i]
            text = page.extract_text()
            if text:
                text_parts.append(f"\n\n--- PAGE {i+1} ---\n\n{text}")

    return "\n".join(text_parts)


def find_section_headers_fannie(text: str) -> list[tuple[str, int]]:
    """
    Find Fannie Mae section headers in text.

    Patterns like: B5-6-01, A1-1-01, C1-2-03, etc.
    """
    # Pattern: Letter + Number + hyphen + Number + hyphen + Number + Number
    pattern = r'\b([A-E]\d+-\d+-\d+)\b'
    matches = []

    for match in re.finditer(pattern, text):
        matches.append((match.group(1), match.start()))

    return matches


def find_section_headers_freddie(text: str) -> list[tuple[str, int]]:
    """
    Find Freddie Mac section headers in text.

    Patterns like: 4501.5, 5201.1, etc.
    """
    # Pattern: 4 digits + dot + 1-2 digits
    pattern = r'\b(\d{4}\.\d{1,2})\b'
    matches = []

    for match in re.finditer(pattern, text):
        matches.append((match.group(1), match.start()))

    return matches


def analyze_pdf_structure(pdf_path: Path, is_fannie: bool = True) -> dict:
    """Analyze the structure of a guide PDF."""
    print(f"\nAnalyzing: {pdf_path.name}")

    # Get basic info
    info = extract_pdf_info(pdf_path)
    print(f"  Total pages: {info['pages']}")

    # Extract sample text (first 50 pages for analysis)
    print("  Extracting sample text...")
    sample_text = extract_sample(pdf_path, start_page=0, num_pages=50)

    # Find section headers
    if is_fannie:
        headers = find_section_headers_fannie(sample_text)
        print(f"  Found {len(headers)} Fannie Mae section references in sample")
    else:
        headers = find_section_headers_freddie(sample_text)
        print(f"  Found {len(headers)} Freddie Mac section references in sample")

    # Get unique sections
    unique_sections = sorted(set(h[0] for h in headers))
    print(f"  Unique sections in sample: {len(unique_sections)}")
    if unique_sections[:10]:
        print(f"  First 10: {unique_sections[:10]}")

    return {
        "info": info,
        "sample_sections": unique_sections,
        "sample_text_length": len(sample_text),
    }


def save_full_text(pdf_path: Path, output_name: str):
    """Extract and save full text from a PDF."""
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{output_name}_full.txt"

    print(f"\nExtracting full text from: {pdf_path.name}")
    text = extract_full_text(pdf_path)

    print(f"  Total characters: {len(text):,}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"  Saved to: {output_path}")
    return output_path


def main():
    """Main entry point."""
    print("=" * 60)
    print("SAGE Guide PDF Parser")
    print("=" * 60)

    # Check if PDFs exist
    fannie_exists = FANNIE_PDF.exists()
    freddie_exists = FREDDIE_PDF.exists()

    print(f"\nFannie Mae PDF: {'Found' if fannie_exists else 'NOT FOUND'}")
    print(f"  Path: {FANNIE_PDF}")

    print(f"\nFreddie Mac PDF: {'Found' if freddie_exists else 'NOT FOUND'}")
    print(f"  Path: {FREDDIE_PDF}")

    if not fannie_exists and not freddie_exists:
        print("\nNo PDFs found. Please download them to your Downloads folder.")
        return

    # Analyze structure
    print("\n" + "=" * 60)
    print("ANALYZING PDF STRUCTURE")
    print("=" * 60)

    if fannie_exists:
        fannie_analysis = analyze_pdf_structure(FANNIE_PDF, is_fannie=True)

    if freddie_exists:
        freddie_analysis = analyze_pdf_structure(FREDDIE_PDF, is_fannie=False)

    # Ask user if they want to extract full text
    print("\n" + "=" * 60)
    print("EXTRACTION OPTIONS")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Extract full text from Fannie Mae PDF")
    print("  2. Extract full text from Freddie Mac PDF")
    print("  3. Extract both")
    print("  4. Exit (just analysis)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1" and fannie_exists:
        save_full_text(FANNIE_PDF, "fannie_mae_selling_guide")
    elif choice == "2" and freddie_exists:
        save_full_text(FREDDIE_PDF, "freddie_mac_guide")
    elif choice == "3":
        if fannie_exists:
            save_full_text(FANNIE_PDF, "fannie_mae_selling_guide")
        if freddie_exists:
            save_full_text(FREDDIE_PDF, "freddie_mac_guide")
    else:
        print("\nExiting without full extraction.")

    print("\nDone!")


if __name__ == "__main__":
    main()
