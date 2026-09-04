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
from collections.abc import Callable
from typing import Any

from rag_ai.knowledge import InMemoryKnowledgePipeline, TokenChunker


def chunked(
    *,
    max_tokens: int = 512,
    overlap: int = 50,
    arg_name: str = "content",
) -> Callable:
    """Decorator that chunks a text argument before passing it to the function.

    The decorated function receives a ``list[str]`` of chunks instead of
    the original string for the parameter named *arg_name*. If the
    argument is already a list, it is passed through unchanged.
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
    """Decorator that injects search results as additional context."""

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
                except RuntimeError:
                    results = asyncio.run(pipeline.query(query_value, limit=top_k))
                else:
                    raise RuntimeError("event loop already running")
                bound.arguments[context_arg] = [r.content for r in results]
            return fn(*bound.args, **bound.kwargs)

        return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper

    return decorator


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
