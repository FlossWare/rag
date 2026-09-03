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

No automatic document ingestion, indexing, or side effects occur on import. Components are explicitly created and invoked by callers.

## ADR-0006: Cross-Cutting Decorators

Cross-cutting decorators are kept separate from core business logic and are used only where they provide a clear composition benefit.

## ADR-0008: Free-First

The composition layer keeps its dependency footprint minimal. Optional infrastructure integrations should remain optional rather than becoming mandatory runtime dependencies.

## ADR-0009: Core Principles

The repository follows modular, composable design with contracts over implementations. Reusable capabilities are being extracted into dedicated repositories rather than duplicated inside the RAG composition layer.

## ADR-0017: Agent-Neutral

RAG composition has no dependency on a particular agent framework or orchestration runtime. It can be consumed by applications, agents, workflows, and test harnesses.

## ADR-0020: Capability-Protocol Separation

Chunking, storage, retrieval, embedding, and other capabilities are independently replaceable. Transport bindings and application orchestration belong outside those foundational capability implementations.
