#!/usr/bin/env python3
"""Claude Code hook: auto-chunk large files before processing.

Usage as a post-read hook in .claude/hooks/post-tool-read.py:
    python3 examples/claude_code_hook.py "$FILE_PATH"
"""
from __future__ import annotations

import sys

from rag_ai import TokenChunker


def main():
    if len(sys.argv) < 2:
        print("Usage: claude_code_hook.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path) as f:
            content = f.read()
    except (FileNotFoundError, IsADirectoryError):
        sys.exit(0)

    if len(content) < 10_000:
        sys.exit(0)

    chunker = TokenChunker(max_tokens=2000, overlap_tokens=200)
    chunks = chunker.chunk(content)

    print(f"[rag-ai] {file_path}: {len(content):,} chars -> {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        word_count = len(chunk.split())
        print(f"  Chunk {i + 1}: {word_count} words")


if __name__ == "__main__":
    main()
