"""RAG composition facade with compatibility exports."""

from __future__ import annotations

from retrieval import RetrievalResult
from storage import ChunkRecord, DocumentRecord, EmbeddingRecord

from rag_ai.decorators import chunked, searchable
from rag_ai.knowledge import InMemoryKnowledgePipeline, TokenChunker
from rag_ai.rag import DocumentIngester, EmbeddingStore, HybridSearcher

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
