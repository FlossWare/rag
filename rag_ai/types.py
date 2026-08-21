"""Shared data types for rag-ai."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RetrievalResult:
    """A single retrieval result from a RAG search."""

    content: str
    score: float
    source: str
    chunk_id: str
    metadata: dict = field(default_factory=dict)
