"""Compatibility adapters for the standalone RAG capabilities.

The implementation now lives in the ``chunking``, ``storage``, and
``retrieval`` packages. These adapters preserve the original rag-ai API while
keeping the composition layer thin.
"""

from __future__ import annotations

import math
import uuid

from retrieval import InMemoryRetriever, RetrievalResult
from storage import (
    ChunkRecord,
    DocumentRecord,
    EmbeddingRecord,
    InMemoryStorage,
)
from chunking import TokenChunker as CanonicalTokenChunker


class DocumentIngester:
    """Compatibility facade composing chunking and storage."""

    def __init__(self, *, max_tokens: int = 512, overlap: int = 50) -> None:
        self._chunker = CanonicalTokenChunker()
        self._storage = InMemoryStorage()
        self._max_tokens = max_tokens
        self._overlap = overlap
        self._hash_index: dict[str, str] = {}

    async def ingest(
        self,
        content: str,
        *,
        metadata: dict | None = None,
        provenance: dict | None = None,
    ) -> str:
        import hashlib

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        existing = self._hash_index.get(content_hash)
        if existing is not None:
            return existing

        document_id = str(uuid.uuid4())
        chunks = self._chunker.chunk(
            content,
            document_id=document_id,
            max_tokens=self._max_tokens,
            overlap=self._overlap,
            metadata=metadata,
            provenance=provenance,
        )
        records = [
            ChunkRecord(
                id=c.id,
                document_id=c.document_id,
                content=c.content,
                sequence=c.sequence,
                token_count=c.token_count,
                start_offset=c.start_offset,
                end_offset=c.end_offset,
                metadata=dict(c.metadata),
                provenance=dict(c.provenance),
            )
            for c in chunks
        ]
        await self._storage.put_document(
            DocumentRecord(
                id=document_id,
                content=content,
                chunk_ids=[c.id for c in records],
                metadata=dict(metadata or {}),
                provenance=dict(provenance or {}),
                content_hash=content_hash,
            )
        )
        for chunk in records:
            await self._storage.put_chunk(chunk)
        self._hash_index[content_hash] = document_id
        return document_id

    async def get_document(self, doc_id: str) -> DocumentRecord | None:
        return await self._storage.get_document(doc_id)

    async def get_chunk(self, chunk_id: str) -> ChunkRecord | None:
        return await self._storage.get_chunk(chunk_id)

    async def get_chunks_for_document(self, doc_id: str) -> list[ChunkRecord]:
        return await self._storage.get_chunks_for_document(doc_id)

    async def delete_document(self, doc_id: str) -> bool:
        document = await self._storage.get_document(doc_id)
        if document is None:
            return False
        result = await self._storage.delete_document(doc_id)
        if result:
            self._hash_index.pop(document.content_hash, None)
        return result

    @property
    def document_count(self) -> int:
        return len(self._storage.documents)

    @property
    def chunk_count(self) -> int:
        return len(self._storage.chunks)


class EmbeddingStore:
    """Compatibility facade storing embeddings through the storage capability."""

    def __init__(self, *, dim: int = 64) -> None:
        self._dim = dim
        self._storage = InMemoryStorage()

    async def store(
        self,
        chunk_id: str,
        text: str,
        *,
        vector: list[float] | None = None,
        metadata: dict | None = None,
    ) -> str:
        embedding_id = str(uuid.uuid4())
        vector = vector if vector is not None else _simple_embedding(text, self._dim)
        await self._storage.put_embedding(
            EmbeddingRecord(
                id=embedding_id,
                chunk_id=chunk_id,
                vector=list(vector),
                metadata=dict(metadata or {}),
            )
        )
        return embedding_id

    async def search(
        self,
        query: str,
        *,
        vector: list[float] | None = None,
        limit: int = 10,
    ) -> list[tuple[str, float]]:
        qvec = vector if vector is not None else _simple_embedding(query, self._dim)
        return await self._storage.search(qvec, limit=limit)

    async def get_embedding(self, chunk_id: str) -> EmbeddingRecord | None:
        return await self._storage.get_embedding(chunk_id)

    async def delete(self, chunk_id: str) -> bool:
        return await self._storage.delete_embedding(chunk_id)

    @property
    def count(self) -> int:
        return len(self._storage.embeddings)


class HybridSearcher:
    """Compatibility facade over the retrieval capability."""

    def __init__(
        self,
        ingester: DocumentIngester,
        embedding_store: EmbeddingStore,
        *,
        keyword_weight: float = 0.5,
        vector_weight: float = 0.5,
        rrf_k: int = 60,
    ) -> None:
        self._ingester = ingester
        self._embedding_store = embedding_store
        self._keyword_weight = keyword_weight
        self._vector_weight = vector_weight
        self._rrf_k = rrf_k

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        mode: str = "hybrid",
    ) -> list[RetrievalResult]:
        retriever = InMemoryRetriever(
            keyword_weight=self._keyword_weight,
            vector_weight=self._vector_weight,
            rrf_k=self._rrf_k,
        )
        for chunk in self._ingester._storage.chunks.values():
            retriever.add_chunk(
                chunk.id,
                chunk.content,
                source=chunk.document_id,
                metadata=chunk.metadata,
            )
        for embedding in self._embedding_store._storage.embeddings.values():
            retriever.add_vector(embedding.chunk_id, embedding.vector)

        return await retriever.search(query, limit=limit, mode=mode)


def _simple_embedding(text: str, dim: int = 64) -> list[float]:
    """Deterministic dependency-free fallback vector for compatibility."""
    vector = [0.0] * dim
    lower = text.lower()
    for i in range(len(lower) - 1):
        pair = lower[i : i + 2]
        vector[sum(ord(c) for c in pair) % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]
