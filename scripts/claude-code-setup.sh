#!/bin/bash
# Add rag-ai integration to your CLAUDE.md
set -e

CLAUDE_MD="${CLAUDE_MD:-./CLAUDE.md}"

if [ ! -f "$CLAUDE_MD" ]; then
    echo "Creating $CLAUDE_MD"
    touch "$CLAUDE_MD"
fi

cat >> "$CLAUDE_MD" << 'EOF'

## RAG Integration (rag-ai)

This project uses [rag-ai](https://github.com/FlossWare/rag-ai) for document chunking and retrieval.

**Install:** `pip install "git+https://github.com/FlossWare/rag-ai.git"`

**Key imports:**
```python
from rag_ai import TokenChunker, InMemoryKnowledgePipeline, chunked, searchable
```

**Usage patterns:**
- Chunk large documents: `TokenChunker(max_tokens=2000).chunk(text)`
- Build searchable knowledge base: `InMemoryKnowledgePipeline()`
- Use `@chunked` decorator to auto-chunk text arguments
- Use `@searchable` decorator for async functions needing retrieval
- Zero external dependencies (stdlib only)
EOF

echo "Added rag-ai integration to $CLAUDE_MD"
