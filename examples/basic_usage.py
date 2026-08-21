#!/usr/bin/env python3
"""Basic rag-ai usage: chunk documents and search with hybrid retrieval."""
from __future__ import annotations

import asyncio

from rag_ai import InMemoryKnowledgePipeline, TokenChunker


async def main():
    # 1. Chunk a large document
    chunker = TokenChunker(max_tokens=100, overlap_tokens=20)
    document = """
    Python is a high-level, general-purpose programming language.
    Its design philosophy emphasizes code readability with the use of
    significant indentation. Python is dynamically typed and garbage-collected.
    It supports multiple programming paradigms, including structured,
    object-oriented, and functional programming.

    Python was conceived in the late 1980s by Guido van Rossum at Centrum
    Wiskunde & Informatica (CWI) in the Netherlands as a successor to the
    ABC programming language. Its implementation began in December 1989.
    """

    chunks = chunker.chunk(document)
    print(f"Chunked document into {len(chunks)} pieces:")
    for i, chunk in enumerate(chunks):
        print(f"  [{i + 1}] {chunk[:60]}...")

    # 2. Build a searchable knowledge base
    pipeline = InMemoryKnowledgePipeline()
    await pipeline.ingest("python-overview", document)
    await pipeline.ingest(
        "rust-overview",
        "Rust is a multi-paradigm, general-purpose programming language "
        "that emphasizes performance, type safety, and concurrency.",
    )

    # 3. Search the knowledge base
    results = await pipeline.query("programming language for safety", top_k=3)
    print(f"\nSearch results for 'programming language for safety':")
    for r in results:
        print(f"  Score: {r.score:.3f} | {r.chunk_id}: {r.text[:80]}...")


if __name__ == "__main__":
    asyncio.run(main())
