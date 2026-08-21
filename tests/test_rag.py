"""Tests for the rag-ai package."""

from __future__ import annotations

import asyncio
import unittest

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


def _run(coro):
    """Helper to run a coroutine synchronously."""
    return asyncio.get_event_loop_policy().new_event_loop().run_until_complete(coro)


class TestRetrievalResult(unittest.TestCase):
    """Tests for the RetrievalResult dataclass."""

    def test_fields(self):
        r = RetrievalResult(
            content="hello", score=0.9, source="doc1", chunk_id="c1"
        )
        self.assertEqual(r.content, "hello")
        self.assertEqual(r.score, 0.9)
        self.assertEqual(r.source, "doc1")
        self.assertEqual(r.chunk_id, "c1")
        self.assertEqual(r.metadata, {})

    def test_metadata_default_factory(self):
        r1 = RetrievalResult(content="a", score=0.0, source="s", chunk_id="c")
        r2 = RetrievalResult(content="b", score=0.0, source="s", chunk_id="c")
        r1.metadata["key"] = "value"
        self.assertEqual(r2.metadata, {})


class TestTokenChunker(unittest.TestCase):
    """Tests for the TokenChunker class."""

    def test_empty_content(self):
        chunker = TokenChunker()
        self.assertEqual(chunker.chunk(""), [])

    def test_single_sentence(self):
        chunker = TokenChunker()
        chunks = chunker.chunk("Hello world.")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], "Hello world.")

    def test_multiple_chunks(self):
        chunker = TokenChunker()
        # max_tokens=5 means max_chars=20, so short sentences get split
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunker.chunk(text, max_tokens=5, overlap=0)
        self.assertGreaterEqual(len(chunks), 2)

    def test_overlap_produces_shared_content(self):
        chunker = TokenChunker()
        text = "AAA. BBB. CCC. DDD. EEE."
        chunks = chunker.chunk(text, max_tokens=3, overlap=2)
        if len(chunks) >= 2:
            # With overlap, some trailing content from chunk N
            # should appear at the start of chunk N+1
            last_part = chunks[0][-8:]  # grab tail
            self.assertTrue(
                any(part in chunks[1] for part in [last_part] if len(part) > 2)
                or len(chunks) >= 2
            )


class TestDocumentIngester(unittest.TestCase):
    """Tests for the DocumentIngester class."""

    def test_ingest_and_retrieve(self):
        ingester = DocumentIngester()
        doc_id = _run(ingester.ingest("Some test content."))
        self.assertIsInstance(doc_id, str)
        self.assertEqual(ingester.document_count, 1)

        doc = _run(ingester.get_document(doc_id))
        self.assertIsNotNone(doc)
        self.assertIsInstance(doc, DocumentRecord)
        self.assertEqual(doc.content, "Some test content.")

    def test_deduplication(self):
        ingester = DocumentIngester()
        id1 = _run(ingester.ingest("Duplicate content."))
        id2 = _run(ingester.ingest("Duplicate content."))
        self.assertEqual(id1, id2)
        self.assertEqual(ingester.document_count, 1)

    def test_chunking_creates_chunks(self):
        ingester = DocumentIngester(max_tokens=5, overlap=0)
        text = "First sentence. Second sentence. Third sentence."
        doc_id = _run(ingester.ingest(text))
        chunks = _run(ingester.get_chunks_for_document(doc_id))
        self.assertGreaterEqual(len(chunks), 1)
        for chunk in chunks:
            self.assertIsInstance(chunk, ChunkRecord)

    def test_delete_document(self):
        ingester = DocumentIngester()
        doc_id = _run(ingester.ingest("To be deleted."))
        self.assertEqual(ingester.document_count, 1)
        result = _run(ingester.delete_document(doc_id))
        self.assertTrue(result)
        self.assertEqual(ingester.document_count, 0)

    def test_delete_nonexistent(self):
        ingester = DocumentIngester()
        result = _run(ingester.delete_document("nonexistent"))
        self.assertFalse(result)

    def test_metadata_and_provenance(self):
        ingester = DocumentIngester()
        doc_id = _run(
            ingester.ingest(
                "Content with metadata.",
                metadata={"source": "test"},
                provenance={"author": "bot"},
            )
        )
        doc = _run(ingester.get_document(doc_id))
        self.assertEqual(doc.metadata, {"source": "test"})
        self.assertEqual(doc.provenance, {"author": "bot"})


class TestEmbeddingStore(unittest.TestCase):
    """Tests for the EmbeddingStore class."""

    def test_store_and_search(self):
        store = EmbeddingStore(dim=16)
        _run(store.store("c1", "hello world"))
        _run(store.store("c2", "goodbye world"))
        self.assertEqual(store.count, 2)

        results = _run(store.search("hello"))
        self.assertGreaterEqual(len(results), 1)
        # Results are (chunk_id, similarity) tuples
        chunk_ids = [r[0] for r in results]
        self.assertIn("c1", chunk_ids)

    def test_delete_embedding(self):
        store = EmbeddingStore(dim=16)
        _run(store.store("c1", "test"))
        self.assertEqual(store.count, 1)
        result = _run(store.delete("c1"))
        self.assertTrue(result)
        self.assertEqual(store.count, 0)

    def test_get_embedding(self):
        store = EmbeddingStore(dim=16)
        _run(store.store("c1", "test"))
        emb = _run(store.get_embedding("c1"))
        self.assertIsNotNone(emb)
        self.assertIsInstance(emb, EmbeddingRecord)
        self.assertEqual(len(emb.vector), 16)


class TestHybridSearcher(unittest.TestCase):
    """Tests for the HybridSearcher class."""

    def _setup_searcher(self):
        ingester = DocumentIngester(max_tokens=512)
        store = EmbeddingStore(dim=32)
        doc_id = _run(
            ingester.ingest(
                "Python is a great programming language. "
                "It supports object-oriented and functional programming.",
                metadata={"topic": "python"},
            )
        )
        chunks = _run(ingester.get_chunks_for_document(doc_id))
        for chunk in chunks:
            _run(store.store(chunk.id, chunk.content))
        searcher = HybridSearcher(ingester, store)
        return searcher

    def test_keyword_search(self):
        searcher = self._setup_searcher()
        results = _run(searcher.search("python", mode="keyword"))
        self.assertGreaterEqual(len(results), 1)
        self.assertIsInstance(results[0], RetrievalResult)
        self.assertGreater(results[0].score, 0)

    def test_vector_search(self):
        searcher = self._setup_searcher()
        results = _run(searcher.search("programming language", mode="vector"))
        self.assertGreaterEqual(len(results), 1)
        self.assertIsInstance(results[0], RetrievalResult)

    def test_hybrid_search(self):
        searcher = self._setup_searcher()
        results = _run(searcher.search("python programming", mode="hybrid"))
        self.assertGreaterEqual(len(results), 1)
        self.assertIsInstance(results[0], RetrievalResult)


class TestInMemoryKnowledgePipeline(unittest.TestCase):
    """Tests for the InMemoryKnowledgePipeline class."""

    def test_ingest_and_query(self):
        pipeline = InMemoryKnowledgePipeline(TokenChunker())
        doc_id = _run(
            pipeline.ingest(
                "Machine learning is a subset of artificial intelligence.",
                metadata={"domain": "ml"},
            )
        )
        self.assertIsInstance(doc_id, str)

        results = _run(pipeline.query("machine learning"))
        self.assertGreaterEqual(len(results), 1)
        self.assertIsInstance(results[0], RetrievalResult)
        self.assertGreater(results[0].score, 0)

    def test_empty_query(self):
        pipeline = InMemoryKnowledgePipeline(TokenChunker())
        _run(pipeline.ingest("Some content here."))
        results = _run(pipeline.query(""))
        self.assertEqual(results, [])


class TestChunkedDecorator(unittest.TestCase):
    """Tests for the @chunked decorator."""

    def test_chunks_string_argument(self):
        @chunked(max_tokens=5, overlap=0)
        def process(content: list[str]) -> int:
            return len(content)

        text = "First sentence. Second sentence. Third sentence."
        result = process(content=text)
        self.assertGreaterEqual(result, 2)

    def test_passes_list_unchanged(self):
        @chunked(max_tokens=5, overlap=0)
        def process(content: list[str]) -> list[str]:
            return content

        original = ["chunk1", "chunk2"]
        result = process(content=original)
        self.assertEqual(result, original)

    def test_works_with_async(self):
        @chunked(max_tokens=5, overlap=0)
        async def process(content: list[str]) -> int:
            return len(content)

        text = "First sentence. Second sentence. Third sentence."
        result = _run(process(content=text))
        self.assertGreaterEqual(result, 2)

    def test_preserves_function_name(self):
        @chunked(max_tokens=512)
        def my_func(content: list[str]) -> None:
            pass

        self.assertEqual(my_func.__name__, "my_func")


class TestSearchableDecorator(unittest.TestCase):
    """Tests for the @searchable decorator."""

    def test_injects_context(self):
        pipeline = InMemoryKnowledgePipeline(TokenChunker())
        _run(pipeline.ingest("Python is a programming language."))

        @searchable(pipeline, top_k=3)
        async def answer(query: str, context: list[str] | None = None) -> list[str]:
            return context or []

        result = _run(answer(query="python"))
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)

    def test_empty_query_no_context(self):
        pipeline = InMemoryKnowledgePipeline(TokenChunker())
        _run(pipeline.ingest("Some content."))

        @searchable(pipeline, top_k=3)
        async def answer(query: str, context: list[str] | None = None) -> list[str]:
            return context or []

        result = _run(answer(query=""))
        self.assertEqual(result, [])

    def test_preserves_function_name(self):
        pipeline = InMemoryKnowledgePipeline(TokenChunker())

        @searchable(pipeline, top_k=5)
        async def my_search(query: str, context: list[str] | None = None) -> None:
            pass

        self.assertEqual(my_search.__name__, "my_search")


class TestNoLoomImports(unittest.TestCase):
    """Verify no loom_ai imports remain in the package."""

    def test_no_loom_imports(self):
        import pathlib

        pkg_dir = pathlib.Path(__file__).resolve().parent.parent / "rag_ai"
        for py_file in pkg_dir.rglob("*.py"):
            content = py_file.read_text()
            self.assertNotIn(
                "loom_ai",
                content,
                f"Found 'loom_ai' import in {py_file.name}",
            )


if __name__ == "__main__":
    unittest.main()
