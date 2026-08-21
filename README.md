# rag-ai

Standalone RAG (Retrieval-Augmented Generation) pipeline with document ingestion, embeddings, and hybrid search. Zero external dependencies -- uses only the Python standard library.

## Install

```bash
pip install -e .
```

## Quickstart

### Document ingestion and hybrid search

```python
import asyncio
from rag_ai import DocumentIngester, EmbeddingStore, HybridSearcher

async def main():
    ingester = DocumentIngester(max_tokens=256)
    store = EmbeddingStore(dim=64)

    # Ingest a document
    doc_id = await ingester.ingest(
        "Python is a versatile programming language. "
        "It supports multiple paradigms including OOP and functional.",
        metadata={"topic": "python"},
    )

    # Store embeddings for each chunk
    for chunk in await ingester.get_chunks_for_document(doc_id):
        await store.store(chunk.id, chunk.content)

    # Search with hybrid mode (keyword + vector fusion)
    searcher = HybridSearcher(ingester, store)
    results = await searcher.search("python programming")

    for r in results:
        print(f"[{r.score:.4f}] {r.content[:80]}")

asyncio.run(main())
```

### Knowledge pipeline (simpler API)

```python
import asyncio
from rag_ai import TokenChunker, InMemoryKnowledgePipeline

async def main():
    pipeline = InMemoryKnowledgePipeline(TokenChunker())
    await pipeline.ingest("Machine learning is a subset of AI.")
    results = await pipeline.query("machine learning")
    for r in results:
        print(f"[{r.score:.1f}] {r.content}")

asyncio.run(main())
```

### Decorators (ADR-0006)

```python
from rag_ai import chunked, searchable, TokenChunker, InMemoryKnowledgePipeline

# Automatically chunk a string argument before processing
@chunked(max_tokens=256, overlap=25)
def process(content: list[str]) -> int:
    return len(content)

count = process(content="A very long document that will be chunked...")

# Inject search-retrieved context into a function
pipeline = InMemoryKnowledgePipeline(TokenChunker())

@searchable(pipeline, top_k=3)
async def answer(query: str, context: list[str] | None = None) -> str:
    snippets = context or []
    return f"Found {len(snippets)} passages for: {query}"
```

## API Overview

| Class / Decorator | Description |
|---|---|
| `RetrievalResult` | Dataclass for search results (content, score, source, chunk_id, metadata) |
| `DocumentIngester` | Ingest documents with chunking, deduplication, and provenance tracking |
| `EmbeddingStore` | Store and search embeddings with cosine similarity |
| `HybridSearcher` | Combine keyword and vector search via Reciprocal Rank Fusion |
| `TokenChunker` | Sentence-aware text chunker with token-bounded overlap |
| `InMemoryKnowledgePipeline` | Simple keyword-scored retrieval over chunked documents |
| `DocumentRecord` | Internal record for an ingested document |
| `ChunkRecord` | Internal record for a text chunk |
| `EmbeddingRecord` | Internal record for an embedding vector |
| `@chunked` | Decorator: auto-chunk string arguments into token-bounded pieces |
| `@searchable` | Decorator: inject search-retrieved context from a pipeline |

## FlossWare Engineering Standards

This package complies with the following [FlossWare Engineering Standards](https://github.com/FlossWare/engineering-standards) ADRs:

| ADR | Title | How |
|-----|-------|-----|
| ADR-0001 | Explicit Opt-In | No side effects on import; all components are explicitly created |
| ADR-0006 | Cross-Cutting Decorators | `@chunked` and `@searchable` decorators |
| ADR-0008 | Free-First | Zero external dependencies (stdlib only) |
| ADR-0009 | Core Principles | Modular, composable components with contracts over implementations |
| ADR-0017 | Agent-Neutral | No agent framework dependency |
| ADR-0020 | Capability-Protocol Separation | Transport-independent RAG capabilities |

See [STANDARDS.md](STANDARDS.md) for full compliance details.

## License

MIT
