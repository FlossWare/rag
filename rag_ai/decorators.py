"""Cross-cutting decorators for RAG pipelines (ADR-0006).

Provides convenience decorators that compose with the core RAG components
without coupling to any specific transport or agent runtime.

Decorators
----------
chunked    -- automatically chunk text arguments before processing
searchable -- augment function calls with search-retrieved context
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Callable

from rag_ai.knowledge import InMemoryKnowledgePipeline, TokenChunker


def chunked(
    *,
    max_tokens: int = 512,
    overlap: int = 50,
    arg_name: str = "content",
) -> Callable:
    """Decorator that chunks a text argument before passing it to the function.

    The decorated function receives a ``list[str]`` of chunks instead of
    the original string for the parameter named *arg_name*.  If the
    argument is already a list, it is passed through unchanged.

    Parameters
    ----------
    max_tokens:
        Maximum token budget per chunk (estimated at 4 chars/token).
    overlap:
        Number of overlapping tokens between consecutive chunks.
    arg_name:
        Name of the parameter whose value should be chunked.

    Example
    -------
    ::

        @chunked(max_tokens=256, overlap=25)
        def process(content: list[str]) -> int:
            return len(content)

        # Passing a long string automatically chunks it:
        n = process(content="A very long document...")
    """
    chunker = TokenChunker()

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = _bind_arguments(fn, args, kwargs)
            value = bound.arguments.get(arg_name)
            if isinstance(value, str):
                bound.arguments[arg_name] = chunker.chunk(
                    value, max_tokens=max_tokens, overlap=overlap
                )
            return fn(*bound.args, **bound.kwargs)

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = _bind_arguments(fn, args, kwargs)
            value = bound.arguments.get(arg_name)
            if isinstance(value, str):
                bound.arguments[arg_name] = chunker.chunk(
                    value, max_tokens=max_tokens, overlap=overlap
                )
            return await fn(*bound.args, **bound.kwargs)

        return async_wrapper if inspect.iscoroutinefunction(fn) else wrapper

    return decorator


def searchable(
    pipeline: InMemoryKnowledgePipeline,
    *,
    top_k: int = 5,
    query_arg: str = "query",
    context_arg: str = "context",
) -> Callable:
    """Decorator that injects search results as additional context.

    Before the decorated function runs, the *query_arg* value is used to
    query the *pipeline*.  The top *top_k* results are injected as a
    ``list[str]`` into the *context_arg* keyword argument.

    Parameters
    ----------
    pipeline:
        An :class:`InMemoryKnowledgePipeline` to search against.
    top_k:
        Maximum number of search results to inject.
    query_arg:
        Name of the parameter containing the search query.
    context_arg:
        Name of the parameter that receives the retrieved context.

    Example
    -------
    ::

        pipeline = InMemoryKnowledgePipeline(TokenChunker())
        # ... ingest documents into pipeline ...

        @searchable(pipeline, top_k=3)
        async def answer(query: str, context: list[str] | None = None) -> str:
            snippets = context or []
            return f"Found {len(snippets)} relevant passages for: {query}"
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = _bind_arguments(fn, args, kwargs)
            query_value = bound.arguments.get(query_arg, "")
            if isinstance(query_value, str) and query_value:
                results = await pipeline.query(query_value, limit=top_k)
                bound.arguments[context_arg] = [r.content for r in results]
            return await fn(*bound.args, **bound.kwargs)

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = _bind_arguments(fn, args, kwargs)
            query_value = bound.arguments.get(query_arg, "")
            if isinstance(query_value, str) and query_value:
                try:
                    asyncio.get_running_loop()
                    raise RuntimeError("event loop already running")
                except RuntimeError:
                    results = asyncio.run(
                        pipeline.query(query_value, limit=top_k)
                    )
                bound.arguments[context_arg] = [r.content for r in results]
            return fn(*bound.args, **bound.kwargs)

        return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper

    return decorator


# -- helpers ------------------------------------------------------------------


def _bind_arguments(
    fn: Callable,
    args: tuple,
    kwargs: dict,
) -> inspect.BoundArguments:
    """Bind positional and keyword arguments, preserving *args/**kwargs."""
    sig = inspect.signature(fn)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    return bound
