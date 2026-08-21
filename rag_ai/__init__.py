"""rag-ai: standalone RAG pipeline with document ingestion, embeddings, and hybrid search."""

from __future__ import annotations

from rag_ai.knowledge import InMemoryKnowledgePipeline, TokenChunker
from rag_ai.rag import (
    ChunkRecord,
    DocumentIngester,
    DocumentRecord,
    EmbeddingRecord,
    EmbeddingStore,
    HybridSearcher,
)
from rag_ai.decorators import chunked, searchable
from rag_ai.types import RetrievalResult

__all__ = [
    "ChunkRecord",
    "DocumentIngester",
    "DocumentRecord",
    "EmbeddingRecord",
    "EmbeddingStore",
    "HybridSearcher",
    "InMemoryKnowledgePipeline",
    "RetrievalResult",
    "TokenChunker",
    "chunked",
    "searchable",
]

__version__ = "0.1"
