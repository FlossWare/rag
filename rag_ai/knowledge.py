"""RAG composition over the standalone chunking, storage, and retrieval capabilities."""

from __future__ import annotations

import hashlib
import uuid

from chunking import TokenChunker as CanonicalTokenChunker
from retrieval import InMemoryRetriever
from retrieval import RetrievalResult
from storage import ChunkRecord, DocumentRecord, InMemoryStorage


class TokenChunker:
    """Backward-compatible text-only facade over the chunking capability."""

    def __init__(self) -> None:
        self._chunker = CanonicalTokenChunker()

    def chunk(self, content: str, *, max_tokens: int = 512, overlap: int = 50) -> list[str]:
        return [
            chunk.content
            for chunk in self._chunker.chunk(
                content, max_tokens=max_tokens, overlap=overlap
            )
        ]


class InMemoryKnowledgePipeline:
    """Compose canonical chunking, storage, and retrieval implementations."""

    def __init__(
        self,
        chunker: TokenChunker | CanonicalTokenChunker | None = None,
        *,
        max_tokens: int = 512,
        overlap: int = 50,
    ) -> None:
        self._chunker = (
            chunker._chunker
            if isinstance(chunker, TokenChunker)
            else chunker or CanonicalTokenChunker()
        )
        self._max_tokens = max_tokens
        self._overlap = overlap
        self._storage = InMemoryStorage()
        self._retriever = InMemoryRetriever()

    async def ingest(self, content: str, *, metadata: dict | None = None) -> str:
        document_id = str(uuid.uuid4())
        chunks = self._chunker.chunk(
            content,
            document_id=document_id,
            max_tokens=self._max_tokens,
            overlap=self._overlap,
            metadata=metadata,
        )
        records = [
            ChunkRecord(
                id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                sequence=chunk.sequence,
                token_count=chunk.token_count,
                start_offset=chunk.start_offset,
                end_offset=chunk.end_offset,
                metadata=dict(chunk.metadata),
                provenance=dict(chunk.provenance),
            )
            for chunk in chunks
        ]
        document = DocumentRecord(
            id=document_id,
            content=content,
            chunk_ids=[chunk.id for chunk in records],
            metadata=dict(metadata or {}),
            content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        )
        await self._storage.put_document(document)
        for chunk in records:
            await self._storage.put_chunk(chunk)
            self._retriever.add_chunk(
                chunk.id,
                chunk.content,
                source=document_id,
                metadata=chunk.metadata,
            )
        return document_id

    async def query(self, question: str, *, limit: int = 10) -> list[RetrievalResult]:
        if not question.strip():
            return []
        return await self._retriever.search(question, limit=limit, mode="keyword")

    @property
    def storage(self) -> InMemoryStorage:
        """Expose the composed storage backend for advanced callers."""
        return self._storage
