#!/usr/bin/env python3
"""Verify rag-ai installation and run a quick smoke test."""
import asyncio
import sys


def main():
    try:
        from rag_ai import (
            ChunkRecord,
            DocumentIngester,
            DocumentRecord,
            EmbeddingRecord,
            EmbeddingStore,
            HybridSearcher,
            InMemoryKnowledgePipeline,
            RetrievalResult,
            TokenChunker,
            chunked,
            searchable,
        )
    except ImportError as e:
        print(f"FAIL: Could not import rag_ai: {e}")
        print("Install: pip install 'git+https://github.com/FlossWare/rag-ai.git'")
        sys.exit(1)

    import rag_ai

    print(f"rag-ai v{rag_ai.__version__} installed successfully")
    print(f"Exports: {len(rag_ai.__all__)} public symbols")

    # Smoke test: chunk some text
    chunker = TokenChunker(max_tokens=50, overlap_tokens=10)
    text = "The quick brown fox jumps over the lazy dog. " * 20
    chunks = chunker.chunk(text)
    print(f"Smoke test: chunked {len(text)} chars into {len(chunks)} chunks")

    # Smoke test: pipeline
    async def test_pipeline():
        pipeline = InMemoryKnowledgePipeline()
        await pipeline.ingest("test", "Hello world, this is a test document.")
        results = await pipeline.query("test", top_k=1)
        return len(results)

    n = asyncio.run(test_pipeline())
    print(f"Smoke test: pipeline query returned {n} result(s)")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
