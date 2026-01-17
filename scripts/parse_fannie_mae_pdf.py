#!/usr/bin/env python3
"""
Parse Fannie Mae Selling Guide from PDF.

This script extracts text from the Fannie Mae Selling Guide PDF and saves
it as structured text files for embedding into Pinecone.

Usage:
    python parse_fannie_mae_pdf.py
"""

import os
import re
import json
from pathlib import Path
from typing import Optional

try:
    import pdfplumber
except ImportError:
    print("Please install pdfplumber: pip install pdfplumber")
    exit(1)

# PDF path
PDF_PATH = Path(os.path.expanduser("~/Downloads/Selling-Guide_12-10-25_Highlight.pdf"))

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "fannie_mae_guide"


def extract_all_text(pdf_path: Path, progress_callback=None) -> str:
    """Extract all text from a PDF."""
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            if progress_callback and i % 100 == 0:
                progress_callback(i, total)

            text = page.extract_text()
            if text:
                text_parts.append(text)

    return '\n\n'.join(text_parts)


def find_sections(text: str) -> list[tuple[str, str, int]]:
    """
    Find section headers in the text.
    Returns list of (section_id, title, position)

    Fannie Mae format: A1-1-01, Title (date) or B5-6-01: Title
    """
    sections = []

    # Pattern for Fannie Mae sections: A1-1-01, B5-6-02, etc.
    # Format: Letter + digit + hyphen + digit(s) + hyphen + digit(s), followed by comma or colon and title
    pattern = re.compile(r'\n([A-E]\d+-\d+(?:\.\d+)?-\d+)[,:\s]+\s*([^\n\(]+)', re.MULTILINE)

    for match in pattern.finditer(text):
        section_id = match.group(1)
        title = match.group(2).strip()
        # Clean up title
        title = re.sub(r'\s*\(\d{2}/\d{2}/\d{4}\)\s*$', '', title)  # Remove date at end
        position = match.start()
        sections.append((section_id, title, position))

    return sections


def split_into_sections(text: str, sections: list[tuple[str, str, int]]) -> dict:
    """
    Split text into sections based on found headers.
    Returns dict of {section_id: {"title": str, "content": str}}
    """
    result = {}

    for i, (section_id, title, start_pos) in enumerate(sections):
        # End position is start of next section, or end of text
        if i + 1 < len(sections):
            end_pos = sections[i + 1][2]
        else:
            end_pos = len(text)

        content = text[start_pos:end_pos].strip()

        # Skip if duplicate (keep the one with more content)
        if section_id in result:
            if len(content) <= len(result[section_id]['content']):
                continue

        result[section_id] = {
            "title": title,
            "content": content,
        }

    return result


def save_section(section_id: str, title: str, content: str):
    """Save a section to a text file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create filename - replace dots with hyphens for filesystem safety
    safe_id = section_id.replace('.', '-')
    filename = f"{safe_id}.txt"
    filepath = OUTPUT_DIR / filename

    # Format content with metadata
    output = f"""# {section_id}: {title}
Source: Fannie Mae Selling Guide (PDF)
Section ID: {section_id}

---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

    return filepath


def parse_guide():
    """Parse the entire Fannie Mae Selling Guide."""
    print("=" * 60)
    print("Fannie Mae Selling Guide PDF Parser")
    print("=" * 60)

    if not PDF_PATH.exists():
        print(f"\nERROR: PDF not found at {PDF_PATH}")
        print("Please download the Fannie Mae Selling Guide PDF to your Downloads folder.")
        return

    print(f"\nPDF path: {PDF_PATH}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Get PDF info
    with pdfplumber.open(PDF_PATH) as pdf:
        total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")

    # Extract text
    print("\nExtracting text from PDF...")

    def progress(current, total):
        print(f"  Processing page {current}/{total}...")

    text = extract_all_text(PDF_PATH, progress_callback=progress)
    print(f"Total text extracted: {len(text):,} characters")

    # Find sections
    print("\nFinding sections...")
    sections = find_sections(text)
    print(f"Found {len(sections)} sections")

    if sections:
        print("\nFirst 10 sections found:")
        for section_id, title, _ in sections[:10]:
            print(f"  {section_id}: {title[:50]}...")

    # Split into sections
    print("\nSplitting into sections...")
    section_data = split_into_sections(text, sections)
    print(f"Unique sections: {len(section_data)}")

    # Save sections
    print("\nSaving sections...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clear existing files
    for f in OUTPUT_DIR.glob("*.txt"):
        if not f.name.startswith("_"):
            f.unlink()

    for i, (section_id, data) in enumerate(section_data.items()):
        filepath = save_section(section_id, data['title'], data['content'])
        if i < 10 or i % 50 == 0:
            print(f"  [{i+1}/{len(section_data)}] Saved {filepath.name} ({len(data['content']):,} chars)")

    # Save full text as well (for backup/reference)
    full_text_path = OUTPUT_DIR / "_full_text.txt"
    with open(full_text_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"\nFull text saved to: {full_text_path}")

    # Save metadata
    metadata = {
        "source": "Fannie Mae Selling Guide",
        "pdf_path": str(PDF_PATH),
        "total_pages": total_pages,
        "total_sections": len(section_data),
        "total_characters": len(text),
        "sections": [{"id": sid, "title": data['title']} for sid, data in section_data.items()],
    }

    with open(OUTPUT_DIR / "_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Metadata saved to: {OUTPUT_DIR / '_metadata.json'}")

    print()
    print("=" * 60)
    print("PARSING COMPLETE")
    print("=" * 60)
    print(f"Total sections: {len(section_data)}")
    print(f"Output directory: {OUTPUT_DIR}")


def parse_sample(num_pages: int = 100):
    """Parse just a sample of pages for testing."""
    print("=" * 60)
    print("Fannie Mae Selling Guide PDF Parser (SAMPLE MODE)")
    print("=" * 60)

    if not PDF_PATH.exists():
        print(f"\nERROR: PDF not found at {PDF_PATH}")
        return

    print(f"\nParsing first {num_pages} pages...")

    text_parts = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for i, page in enumerate(pdf.pages[:num_pages]):
            text = page.extract_text()
            if text:
                text_parts.append(text)
            if i % 20 == 0:
                print(f"  Page {i+1}/{num_pages}")

    text = '\n\n'.join(text_parts)
    print(f"\nExtracted {len(text):,} characters")

    # Find sections
    sections = find_sections(text)
    print(f"Found {len(sections)} sections in sample")

    if sections:
        print("\nSections found:")
        for section_id, title, _ in sections[:20]:
            print(f"  {section_id}: {title[:60]}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        parse_sample()
    else:
        parse_guide()
