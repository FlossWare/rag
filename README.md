# rag

RAG (retrieval-augmented generation) composition capability for FlossWare.

RAG composes foundational capabilities such as `chunking`, `storage`, `retrieval`, and model invocation into a reusable retrieval-to-context pipeline. It does **not** own Loom orchestration, Worker/Arbiter execution, provider routing, or durable Knowledge.

## Architectural boundary

```text
document -> chunking -> storage/indexing -> retrieval -> evidence/context
                                                |
                                                v
                                           model-gateway
```

- **chunking** owns deterministic document segmentation.
- **storage** owns persistence contracts and adapters.
- **retrieval** owns lexical/vector/hybrid retrieval and ranking.
- **knowledge** owns durable, versioned knowledge and provenance.
- **model-gateway** owns model/provider invocation.
- **loom-ai** owns Intent, Workers, Arbiters, execution, evaluation, and orchestration.

RAG is therefore a capability composition layer that Loom Workers can use. It must remain independently usable by applications and workflows.

## Status

Active capability repository. Keep implementation focused on RAG composition and integration. Foundational capabilities belong in their dedicated repositories.

## Install

```bash
pip install -e .
```

## Design principle

Expose contracts and composition points; hide provider, storage, and execution mechanisms behind replaceable implementations.

## License

MIT
