#!/usr/bin/env python3
"""
SAGE Guide Ingestion Script

Embeds all parsed guide content into Pinecone vector database for RAG chat.
Supports dynamic file discovery, batched processing, and resume capability.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

# Load .env from backend directory before importing config
from dotenv import load_dotenv
backend_env = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(backend_env)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
BATCH_SIZE = 50  # Vectors per upsert batch
EMBEDDING_BATCH_SIZE = 20  # Texts per embedding API call
RATE_LIMIT_DELAY = 0.5  # Seconds between API calls
CHECKPOINT_FILE = Path(__file__).parent / ".ingest_checkpoint.json"


def parse_file_metadata(file_path: Path) -> Optional[dict]:
    """
    Extract metadata from a guide file's header.

    Expected format:
        # SECTION_ID: Title
        Source: GSE Name
        Section ID: SECTION_ID
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")[:5]

        metadata = {
            "source_file": str(file_path),
            "content": content,
        }

        # Parse header line: # SECTION_ID: Title
        if lines and lines[0].startswith("#"):
            header = lines[0][1:].strip()
            if ":" in header:
                section_id, title = header.split(":", 1)
                metadata["section"] = section_id.strip()
                metadata["title"] = title.strip()

        # Parse source line
        for line in lines:
            if line.startswith("Source:"):
                source = line.replace("Source:", "").strip()
                if "Fannie Mae" in source:
                    metadata["gse"] = "fannie_mae"
                elif "Freddie Mac" in source:
                    metadata["gse"] = "freddie_mac"
                break

        # Validate required fields
        if "section" in metadata and "gse" in metadata:
            return metadata

        return None

    except Exception as e:
        logger.warning(f"Failed to parse {file_path}: {e}")
        return None


def discover_guide_files(data_dir: Path) -> list[dict]:
    """
    Discover all guide files in the data directory.
    Returns list of metadata dicts for each valid file.
    """
    guides = []

    # Directories to scan
    guide_dirs = [
        data_dir / "fannie_mae_guide",
        data_dir / "fannie_mae_servicing_guide",
        data_dir / "freddie_mac_guide",
    ]

    for guide_dir in guide_dirs:
        if not guide_dir.exists():
            logger.warning(f"Directory not found: {guide_dir}")
            continue

        for file_path in guide_dir.glob("*.txt"):
            # Skip metadata and full text files
            if file_path.name.startswith("_"):
                continue

            metadata = parse_file_metadata(file_path)
            if metadata:
                guides.append(metadata)

    return guides


def load_checkpoint() -> set:
    """Load set of already-processed file paths from checkpoint."""
    if CHECKPOINT_FILE.exists():
        try:
            data = json.loads(CHECKPOINT_FILE.read_text())
            return set(data.get("processed_files", []))
        except Exception:
            pass
    return set()


def save_checkpoint(processed_files: set):
    """Save checkpoint of processed files."""
    CHECKPOINT_FILE.write_text(json.dumps({
        "processed_files": list(processed_files),
        "timestamp": time.time(),
    }))


def clear_checkpoint():
    """Clear the checkpoint file."""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


async def chunk_and_embed_batch(
    guides: list[dict],
    embedding_service: EmbeddingService,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[dict]:
    """
    Chunk a batch of guides and generate embeddings.
    Returns list of vectors ready for Pinecone.
    """
    all_chunks = []
    chunk_metadata = []

    # First, chunk all guides
    for guide in guides:
        content = guide["content"]
        chunks = embedding_service.chunk_text(
            content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk["text"])
            chunk_metadata.append({
                "guide": guide,
                "chunk_index": i,
                "text": chunk["text"],
            })

    if not all_chunks:
        return []

    # Generate embeddings in batches
    all_embeddings = []
    for i in range(0, len(all_chunks), EMBEDDING_BATCH_SIZE):
        batch = all_chunks[i:i + EMBEDDING_BATCH_SIZE]

        try:
            embeddings = await embedding_service.embed_texts(batch)
            all_embeddings.extend(embeddings)
        except Exception as e:
            logger.error(f"Embedding failed for batch {i}: {e}")
            # Retry once after delay
            await asyncio.sleep(2)
            try:
                embeddings = await embedding_service.embed_texts(batch)
                all_embeddings.extend(embeddings)
            except Exception as e2:
                logger.error(f"Retry failed: {e2}")
                raise

        # Rate limiting
        if i + EMBEDDING_BATCH_SIZE < len(all_chunks):
            await asyncio.sleep(RATE_LIMIT_DELAY)

    # Create vectors
    vectors = []
    for meta, embedding in zip(chunk_metadata, all_embeddings):
        guide = meta["guide"]
        chunk_id = hashlib.md5(
            f"{guide['section']}_{meta['chunk_index']}_{meta['text'][:50]}".encode()
        ).hexdigest()

        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": {
                "text": meta["text"],
                "gse": guide["gse"],
                "section": guide["section"],
                "title": guide.get("title", ""),
                "chunk_index": meta["chunk_index"],
                "source_file": guide["source_file"],
            },
        })

    return vectors


async def ingest_guides(
    guides: list[dict],
    embedding_service: EmbeddingService,
    pinecone_service: PineconeService,
    namespace: str = "guides",
    resume: bool = True,
) -> dict:
    """
    Ingest all guides into Pinecone with batching and progress tracking.
    """
    # Load checkpoint if resuming
    processed_files = load_checkpoint() if resume else set()

    # Filter out already-processed files
    remaining_guides = [
        g for g in guides
        if g["source_file"] not in processed_files
    ]

    if not remaining_guides:
        logger.info("All files already processed!")
        return {"processed": 0, "vectors": 0, "skipped": len(guides)}

    logger.info(f"Processing {len(remaining_guides)} files ({len(processed_files)} already done)")

    total_vectors = 0

    # Process in batches
    for batch_start in range(0, len(remaining_guides), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(remaining_guides))
        batch = remaining_guides[batch_start:batch_end]

        logger.info(f"Processing batch {batch_start//BATCH_SIZE + 1}: files {batch_start+1}-{batch_end}")

        try:
            # Generate embeddings for batch
            vectors = await chunk_and_embed_batch(batch, embedding_service)

            if vectors:
                # Upsert to Pinecone
                await pinecone_service.upsert_vectors(vectors, namespace=namespace)
                total_vectors += len(vectors)
                logger.info(f"  Upserted {len(vectors)} vectors")

            # Update checkpoint
            for guide in batch:
                processed_files.add(guide["source_file"])
            save_checkpoint(processed_files)

        except Exception as e:
            logger.error(f"Batch failed: {e}")
            save_checkpoint(processed_files)
            raise

        # Progress
        progress = (batch_end / len(remaining_guides)) * 100
        logger.info(f"  Progress: {progress:.1f}% ({batch_end}/{len(remaining_guides)} files)")

    return {
        "processed": len(remaining_guides),
        "vectors": total_vectors,
        "skipped": len(processed_files) - len(remaining_guides),
    }


async def main():
    """Main ingestion function."""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest guides into Pinecone")
    parser.add_argument("--fresh", action="store_true", help="Start fresh (clear checkpoint and namespace)")
    parser.add_argument("--dry-run", action="store_true", help="Just count files without ingesting")
    args = parser.parse_args()

    settings = get_settings()

    # Check required API keys
    if not args.dry_run:
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

    # Discover guide files
    logger.info("Discovering guide files...")
    guides = discover_guide_files(data_dir)

    if not guides:
        logger.error("No guide files found!")
        sys.exit(1)

    # Count by GSE
    fannie_count = sum(1 for g in guides if g["gse"] == "fannie_mae")
    freddie_count = sum(1 for g in guides if g["gse"] == "freddie_mac")

    logger.info(f"Found {len(guides)} guide files:")
    logger.info(f"  Fannie Mae: {fannie_count}")
    logger.info(f"  Freddie Mac: {freddie_count}")

    if args.dry_run:
        logger.info("Dry run complete.")
        return

    # Initialize services
    embedding_service = EmbeddingService()
    pinecone_service = PineconeService()

    # Handle fresh start
    if args.fresh:
        logger.info("Fresh start requested - clearing checkpoint and namespace")
        clear_checkpoint()
        try:
            await pinecone_service.delete_namespace("guides")
            logger.info("Cleared existing vectors in namespace: guides")
        except Exception as e:
            logger.warning(f"Could not clear namespace: {e}")

    # Ingest
    logger.info("Starting ingestion...")
    start_time = time.time()

    result = await ingest_guides(
        guides,
        embedding_service,
        pinecone_service,
        resume=not args.fresh,
    )

    elapsed = time.time() - start_time

    # Print stats
    logger.info("=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Files processed: {result['processed']}")
    logger.info(f"Vectors created: {result['vectors']}")
    logger.info(f"Files skipped (already done): {result['skipped']}")
    logger.info(f"Time elapsed: {elapsed:.1f}s")

    # Get Pinecone stats
    try:
        stats = pinecone_service.get_stats()
        logger.info(f"Pinecone index stats: {stats}")
    except Exception as e:
        logger.warning(f"Could not get Pinecone stats: {e}")

    # Clear checkpoint on successful completion
    clear_checkpoint()
    logger.info("Checkpoint cleared (full ingestion complete)")


if __name__ == "__main__":
    asyncio.run(main())
