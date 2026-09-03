# rag

Standalone RAG (Retrieval-Augmented Generation) composition layer for document ingestion, embeddings, and retrieval. The repository is being refactored so reusable capabilities live in dedicated FlossWare repositories such as `chunking`, `storage`, and `retrieval`.

## Status

This repository is the RAG composition/application layer. Capability implementations are being extracted into independently reusable repositories.

## Install

```bash
pip install -e .
```

## Architecture

```text
document
   |
   v
chunking
   |
   +----> storage
   |
   +----> embedding
   |
   v
retrieval
   |
   v
evidence / context
   |
   v
rag composition
   |
   v
generation
```

The goal is to keep RAG composition separate from foundational capabilities. Chunking, storage, and retrieval should be independently usable by other applications, agents, and workflows.

## FlossWare Engineering Standards

This package complies with the following [FlossWare Engineering Standards](https://github.com/FlossWare/engineering-standards) ADRs:

| ADR | Title | How |
|-----|-------|-----|
| ADR-0001 | Explicit Opt-In | No side effects on import; all components are explicitly created |
| ADR-0006 | Cross-Cutting Decorators | Convenience decorators where appropriate |
| ADR-0008 | Free-First | Zero external dependencies where practical |
| ADR-0009 | Core Principles | Modular, composable components with contracts over implementations |
| ADR-0017 | Agent-Neutral | No agent framework dependency |
| ADR-0020 | Capability-Protocol Separation | Transport-independent RAG capabilities |

See [STANDARDS.md](STANDARDS.md) for full compliance details.

## License

MIT
