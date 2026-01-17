#!/usr/bin/env python3
"""
SAGE Guide Ingestion Script

Embeds scraped guide content into Pinecone vector database for RAG chat.
"""

import asyncio
import hashlib
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Guide metadata for file mapping
GUIDE_METADATA = {
    # Fannie Mae guides
    "B5-6_HomeReady_Overview.txt": {
        "gse": "fannie_mae",
        "section": "B5-6",
        "title": "HomeReady Mortgage Overview",
        "url": "https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B5-Unique-Eligibility-Underwriting-Considerations/Chapter-B5-6-HomeReady-Mortgage/",
    },
    "B5-6-01_HomeReady_Eligibility.txt": {
        "gse": "fannie_mae",
        "section": "B5-6-01",
        "title": "HomeReady Loan and Borrower Eligibility",
        "url": "https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B5-Unique-Eligibility-Underwriting-Considerations/Chapter-B5-6-HomeReady-Mortgage/1032996841/",
    },
    "B5-6-02_HomeReady_Underwriting.txt": {
        "gse": "fannie_mae",
        "section": "B5-6-02",
        "title": "HomeReady Underwriting Considerations",
        "url": "https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B5-Unique-Eligibility-Underwriting-Considerations/Chapter-B5-6-HomeReady-Mortgage/",
    },
    "B5-6-03_HomeReady_Pricing.txt": {
        "gse": "fannie_mae",
        "section": "B5-6-03",
        "title": "HomeReady Pricing and Delivery",
        "url": "https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B5-Unique-Eligibility-Underwriting-Considerations/Chapter-B5-6-HomeReady-Mortgage/",
    },
    "B3-5.1-01_Credit_Scores.txt": {
        "gse": "fannie_mae",
        "section": "B3-5.1-01",
        "title": "Credit Score Requirements",
        "url": "https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B3-Underwriting-Borrowers/Chapter-B3-5-Credit-Assessment/",
    },
    "B3-6-02_DTI_Ratios.txt": {
        "gse": "fannie_mae",
        "section": "B3-6-02",
        "title": "Debt-to-Income Ratios",
        "url": "https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B3-Underwriting-Borrowers/Chapter-B3-6-Liability-Assessment/",
    },
    "B2-1.2-01_LTV_Ratios.txt": {
        "gse": "fannie_mae",
        "section": "B2-1.2-01",
        "title": "Loan-to-Value Ratios",
        "url": "https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B2-Eligibility/Chapter-B2-1-Mortgage-Eligibility/",
    },
    # Freddie Mac guides
    "4501_Home_Possible_Overview.txt": {
        "gse": "freddie_mac",
        "section": "4501",
        "title": "Home Possible Mortgages Overview",
        "url": "https://guide.freddiemac.com/app/guide/section/4501",
    },
    "4501.5_Home_Possible_Eligibility.txt": {
        "gse": "freddie_mac",
        "section": "4501.5",
        "title": "Home Possible Eligibility Requirements",
        "url": "https://guide.freddiemac.com/app/guide/section/4501.5",
    },
    "4501.9_Additional_Requirements.txt": {
        "gse": "freddie_mac",
        "section": "4501.9",
        "title": "Additional Home Possible Requirements",
        "url": "https://guide.freddiemac.com/app/guide/section/4501.9",
    },
    "5201_Credit_Assessment.txt": {
        "gse": "freddie_mac",
        "section": "5201",
        "title": "Credit Assessment",
        "url": "https://guide.freddiemac.com/app/guide/section/5201",
    },
    "5401_Income_Assessment.txt": {
        "gse": "freddie_mac",
        "section": "5401",
        "title": "Income Assessment",
        "url": "https://guide.freddiemac.com/app/guide/section/5401",
    },
}


def extract_url_from_content(content: str) -> str | None:
    """Extract the source URL from the file header."""
    for line in content.split("\n")[:5]:
        if line.startswith("# Source:"):
            return line.replace("# Source:", "").strip()
    return None


async def load_guide_files(data_dir: Path) -> list[dict]:
    """Load all guide files from the data directory."""
    guides = []

    # Process Fannie Mae guides
    fannie_dir = data_dir / "fannie"
    if fannie_dir.exists():
        for file_path in fannie_dir.glob("*.txt"):
            if file_path.name in GUIDE_METADATA:
                content = file_path.read_text(encoding="utf-8")
                metadata = GUIDE_METADATA[file_path.name].copy()
                metadata["source_file"] = str(file_path)
                # Extract URL from file header (more up-to-date than hardcoded)
                extracted_url = extract_url_from_content(content)
                if extracted_url:
                    metadata["url"] = extracted_url
                guides.append({"content": content, "metadata": metadata})
                logger.info(f"Loaded: {file_path.name} ({len(content)} chars)")

    # Process Freddie Mac guides
    freddie_dir = data_dir / "freddie"
    if freddie_dir.exists():
        for file_path in freddie_dir.glob("*.txt"):
            if file_path.name in GUIDE_METADATA:
                content = file_path.read_text(encoding="utf-8")
                metadata = GUIDE_METADATA[file_path.name].copy()
                metadata["source_file"] = str(file_path)
                # Extract URL from file header (more up-to-date than hardcoded)
                extracted_url = extract_url_from_content(content)
                if extracted_url:
                    metadata["url"] = extracted_url
                guides.append({"content": content, "metadata": metadata})
                logger.info(f"Loaded: {file_path.name} ({len(content)} chars)")

    # Also check root scraped_guides directory
    scraped_dir = data_dir / "scraped_guides"
    if scraped_dir.exists():
        for subdir in ["fannie", "freddie"]:
            subdir_path = scraped_dir / subdir
            if subdir_path.exists():
                for file_path in subdir_path.glob("*.txt"):
                    if file_path.name in GUIDE_METADATA:
                        content = file_path.read_text(encoding="utf-8")
                        metadata = GUIDE_METADATA[file_path.name].copy()
                        metadata["source_file"] = str(file_path)
                        # Extract URL from file header
                        extracted_url = extract_url_from_content(content)
                        if extracted_url:
                            metadata["url"] = extracted_url
                        guides.append({"content": content, "metadata": metadata})
                        logger.info(f"Loaded: {file_path.name} ({len(content)} chars)")

    return guides


async def chunk_and_embed_guides(
    guides: list[dict],
    embedding_service: EmbeddingService,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[dict]:
    """Chunk guides and generate embeddings."""
    all_vectors = []

    for guide in guides:
        content = guide["content"]
        metadata = guide["metadata"]

        # Chunk the content
        chunks = embedding_service.chunk_text(
            content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        logger.info(f"Chunked {metadata['section']}: {len(chunks)} chunks")

        # Prepare texts for embedding
        chunk_texts = [chunk["text"] for chunk in chunks]

        # Generate embeddings
        embeddings = await embedding_service.embed_texts(chunk_texts)

        # Create vectors with metadata
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Create unique ID
            chunk_id = hashlib.md5(
                f"{metadata['section']}_{i}_{chunk['text'][:50]}".encode()
            ).hexdigest()

            vector = {
                "id": chunk_id,
                "values": embedding,
                "metadata": {
                    "text": chunk["text"],
                    "gse": metadata["gse"],
                    "section": metadata["section"],
                    "title": metadata["title"],
                    "url": metadata.get("url"),
                    "chunk_index": i,
                    "source_file": metadata.get("source_file"),
                },
            }
            all_vectors.append(vector)

    return all_vectors


async def ingest_to_pinecone(
    vectors: list[dict],
    pinecone_service: PineconeService,
    namespace: str = "guides",
) -> dict:
    """Ingest vectors into Pinecone."""
    logger.info(f"Ingesting {len(vectors)} vectors into Pinecone...")

    # Clear existing vectors in namespace
    try:
        await pinecone_service.delete_namespace(namespace)
        logger.info(f"Cleared existing vectors in namespace: {namespace}")
    except Exception as e:
        logger.warning(f"Could not clear namespace (may not exist): {e}")

    # Upsert vectors
    result = await pinecone_service.upsert_vectors(vectors, namespace=namespace)

    logger.info(f"Ingestion complete: {result}")
    return result


async def main():
    """Main ingestion function."""
    settings = get_settings()

    # Check required API keys
    if not settings.voyage_api_key:
        logger.error("VOYAGE_API_KEY not set. Cannot generate embeddings.")
        sys.exit(1)

    if not settings.pinecone_api_key:
        logger.error("PINECONE_API_KEY not set. Cannot store vectors.")
        sys.exit(1)

    # Find data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)

    logger.info(f"Using data directory: {data_dir}")

    # Initialize services
    embedding_service = EmbeddingService()
    pinecone_service = PineconeService()

    # Load guide files
    logger.info("Loading guide files...")
    guides = await load_guide_files(data_dir)

    if not guides:
        logger.error("No guide files found!")
        sys.exit(1)

    logger.info(f"Loaded {len(guides)} guide files")

    # Chunk and embed
    logger.info("Generating embeddings...")
    vectors = await chunk_and_embed_guides(guides, embedding_service)

    logger.info(f"Generated {len(vectors)} vectors")

    # Ingest to Pinecone
    result = await ingest_to_pinecone(vectors, pinecone_service)

    # Print stats
    stats = pinecone_service.get_stats()
    logger.info(f"Pinecone index stats: {stats}")

    logger.info("Ingestion complete!")


if __name__ == "__main__":
    asyncio.run(main())
