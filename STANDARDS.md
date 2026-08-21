# FlossWare Engineering Standards Compliance

This package adheres to the following ADRs from [FlossWare/engineering-standards](https://github.com/FlossWare/engineering-standards):

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](https://github.com/FlossWare/engineering-standards/blob/main/adr/0001-explicit-opt-in.md) | Explicit Opt-In | Compliant |
| [ADR-0006](https://github.com/FlossWare/engineering-standards/blob/main/adr/0006-cross-cutting-decorators.md) | Cross-Cutting Decorators | Compliant |
| [ADR-0008](https://github.com/FlossWare/engineering-standards/blob/main/adr/0008-free-first.md) | Free-First | Compliant |
| [ADR-0009](https://github.com/FlossWare/engineering-standards/blob/main/adr/0009-core-principles.md) | Core Principles | Compliant |
| [ADR-0017](https://github.com/FlossWare/engineering-standards/blob/main/adr/0017-agent-neutral.md) | Agent-Neutral | Compliant |
| [ADR-0020](https://github.com/FlossWare/engineering-standards/blob/main/adr/0020-capability-protocol-separation.md) | Capability-Protocol Separation | Compliant |

## ADR-0001: Explicit Opt-In

No automatic document ingestion, indexing, or side effects occur on import. Users explicitly create pipeline components (`DocumentIngester`, `EmbeddingStore`, `TokenChunker`, etc.) and invoke their methods. Importing the package does nothing beyond making classes available.

## ADR-0006: Cross-Cutting Decorators

Two convenience decorators are provided in `rag_ai.decorators`:

- **`@chunked(max_tokens=512, overlap=50)`** -- Automatically chunks a string argument into token-bounded pieces before passing them to the decorated function.
- **`@searchable(pipeline, top_k=5)`** -- Injects search-retrieved context from an `InMemoryKnowledgePipeline` into the decorated function.

Both decorators work with sync and async functions.

## ADR-0008: Free-First

Zero external dependencies. The entire package uses only the Python standard library. No pip install beyond the package itself is required.

## ADR-0009: Core Principles

The package follows modular, composable design with contracts over implementations:

- **TokenChunker** -- independent chunking strategy
- **DocumentIngester** -- document storage with pluggable chunk sizes
- **EmbeddingStore** -- vector storage with cosine similarity
- **HybridSearcher** -- composes ingester + embedding store
- **InMemoryKnowledgePipeline** -- composes chunker for simple keyword retrieval

Each component is independently instantiable and composable with others.

## ADR-0017: Agent-Neutral

All components are plain Python classes with no dependency on any agent framework, runtime, or orchestration layer. They work identically whether called from a CLI script, a web server, an agent loop, or a test harness.

## ADR-0020: Capability-Protocol Separation

RAG capabilities (chunking, embedding, search, retrieval) are implemented as transport-independent Python classes. There is no coupling to REST, MCP, gRPC, or any other protocol. Transport bindings are the responsibility of the consuming application.
