# rag-ai Integrations

Install from GitHub:

```bash
pip install "git+https://github.com/FlossWare/rag-ai.git"
```

---

## Claude Code

### CLAUDE.md Snippet

Add to your project's `CLAUDE.md`:

```markdown
## RAG Integration

This project uses `rag-ai` for document chunking and retrieval.

- Chunk long documents before embedding: `from rag_ai import TokenChunker, chunked`
- Search with hybrid retrieval: `from rag_ai import InMemoryKnowledgePipeline, searchable`
- Use `@chunked` decorator to auto-chunk text arguments
- Use `@searchable` decorator to add RAG retrieval to async functions
```

### Hook Example

Create `.claude/hooks/post-tool-read.sh` to auto-chunk large files:

```bash
#!/bin/bash
# Post-read hook: chunk large file reads for context management
FILE_PATH="$1"
if [ -f "$FILE_PATH" ] && [ $(wc -c < "$FILE_PATH") -gt 50000 ]; then
    python3 -c "
from rag_ai import TokenChunker
chunker = TokenChunker(max_tokens=2000, overlap_tokens=200)
with open('$FILE_PATH') as f:
    chunks = chunker.chunk(f.read())
print(f'File chunked into {len(chunks)} segments for processing')
for i, c in enumerate(chunks):
    print(f'--- Chunk {i+1}/{len(chunks)} ({len(c.split())} words) ---')
"
fi
```

### Skill Example

Create `.claude/skills/rag-search.md`:

```markdown
---
name: rag-search
description: Search project knowledge base using hybrid retrieval
---

Use rag-ai to search the project knowledge base:

\```python
import asyncio
from rag_ai import InMemoryKnowledgePipeline

async def search(query: str):
    pipeline = InMemoryKnowledgePipeline()
    # Ingest project docs
    await pipeline.ingest("README.md", open("README.md").read())
    results = await pipeline.query(query, top_k=5)
    return results

results = asyncio.run(search("your query here"))
\```
```

---

## OpenAI Codex

### AGENTS.md Snippet

```markdown
## Tools

### Document Chunking
When processing large documents, use rag-ai:
- Install: `pip install "git+https://github.com/FlossWare/rag-ai.git"`
- Chunk: `TokenChunker(max_tokens=2000).chunk(text)`
- Search: `InMemoryKnowledgePipeline` for hybrid retrieval
```

### Tool Definition

```python
from rag_ai import TokenChunker, InMemoryKnowledgePipeline

# Chunk documents for context window management
chunker = TokenChunker(max_tokens=2000, overlap_tokens=200)
chunks = chunker.chunk(large_document)

# Build searchable knowledge base
pipeline = InMemoryKnowledgePipeline()
await pipeline.ingest("doc.md", content)
results = await pipeline.query("find relevant sections", top_k=5)
```

---

## Cursor

### .cursorrules Snippet

Add to your `.cursorrules`:

```
When working with large documents or knowledge bases, use the rag-ai package:

- Import: from rag_ai import TokenChunker, InMemoryKnowledgePipeline, chunked, searchable
- Chunk large text: TokenChunker(max_tokens=2000).chunk(text)
- Build RAG pipeline: InMemoryKnowledgePipeline()
- Use @chunked decorator to auto-chunk function arguments
- Use @searchable decorator for async functions needing retrieval
- Zero dependencies - stdlib only
- Install: pip install "git+https://github.com/FlossWare/rag-ai.git"
```

### Cursor Composer

When using Cursor Composer for multi-file edits involving document processing:

```python
from rag_ai import TokenChunker, chunked

@chunked(max_tokens=1500, arg_name="content")
async def process_document(content: str) -> str:
    # Each chunk is processed independently
    return f"Processed: {content[:100]}..."
```

---

## Crush

### Configuration

```python
# crush.config.py
from rag_ai import InMemoryKnowledgePipeline, TokenChunker

# Register RAG tools
chunker = TokenChunker(max_tokens=2000, overlap_tokens=200)
pipeline = InMemoryKnowledgePipeline()

async def rag_search(query: str, top_k: int = 5):
    """Search project knowledge base."""
    return await pipeline.query(query, top_k=top_k)

async def chunk_document(text: str):
    """Chunk a document for processing."""
    return chunker.chunk(text)
```

---

## Generic Python Agent

### Basic asyncio Integration

```python
import asyncio
from rag_ai import InMemoryKnowledgePipeline, TokenChunker

async def build_knowledge_base(docs: dict[str, str]):
    pipeline = InMemoryKnowledgePipeline()
    for name, content in docs.items():
        await pipeline.ingest(name, content)
    return pipeline

async def main():
    docs = {
        "readme": open("README.md").read(),
        "api": open("API.md").read(),
    }
    kb = await build_knowledge_base(docs)
    results = await kb.query("How do I configure the router?", top_k=3)
    for r in results:
        print(f"Score: {r.score:.3f} | {r.chunk_id}: {r.text[:80]}...")

asyncio.run(main())
```

### Decorator Patterns

```python
from rag_ai import chunked, searchable

@chunked(max_tokens=1500, arg_name="document")
async def summarize(document: str) -> str:
    # Called once per chunk automatically
    return await llm.chat(f"Summarize: {document}")

@searchable(pipeline=my_pipeline, query_arg="question", top_k=3)
async def answer(question: str, context: list[str] | None = None) -> str:
    # context is auto-populated with search results
    ctx = "\n".join(context or [])
    return await llm.chat(f"Context: {ctx}\nQuestion: {question}")
```

---

## Cross-Package Integration

### rag-ai + observability-ai

Track chunking and search performance:

```python
from rag_ai import InMemoryKnowledgePipeline, chunked
from observability_ai import ExecutionTelemetry, track_execution

telemetry = ExecutionTelemetry()

@track_execution(telemetry=telemetry, name="rag-search")
@chunked(max_tokens=1500, arg_name="text")
async def search_and_track(text: str) -> str:
    pipeline = InMemoryKnowledgePipeline()
    await pipeline.ingest("input", text)
    results = await pipeline.query("key points", top_k=3)
    return str(results)
```

### rag-ai + security-ai

Redact secrets before ingesting into knowledge base:

```python
from rag_ai import InMemoryKnowledgePipeline
from security_ai import SecretsMask

mask = SecretsMask()
pipeline = InMemoryKnowledgePipeline()

async def safe_ingest(name: str, content: str):
    clean_content = mask.redact(content)
    await pipeline.ingest(name, clean_content)
```

### Recommended Decorator Stack Order

```python
@track_execution(telemetry=t)    # outermost: track total time
@mask_secrets(mask=m)            # redact secrets from output
@chunked(max_tokens=1500)       # chunk input text
async def process(text: str):
    ...
```
