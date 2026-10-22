"""Bounded JSON-domain checks only; no interpretation of payload vocabulary."""

import math

MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 10000
MAX_JSON_CHARACTERS = 1000000


def json_domain_issues(
    value: object,
    max_nodes: int = MAX_JSON_NODES,
    max_depth: int = MAX_JSON_DEPTH,
    max_characters: int = MAX_JSON_CHARACTERS,
) -> tuple[str, ...]:
    """Validate JSON types, Unicode and finite numbers without coercion or recursion.

    Depth, node and character bounds apply to the whole supplied value. A
    cycle or exceeded bound is one named refusal, never a RecursionError.
    """

    pending: list[tuple[object, str, int, frozenset[int]]] = [
        (value, "$", 0, frozenset())
    ]
    errors: list[str] = []
    visited = 0
    characters = 0
    while pending:
        item, path, depth, parents = pending.pop()
        visited += 1
        if visited > max_nodes:
            errors.append("JSON node limit exceeded")
            break
        if depth > max_depth:
            errors.append(f"{path}: JSON depth limit exceeded")
            continue
        if type(item) is str:
            characters += len(item)
            try:
                item.encode("utf-8")
            except UnicodeEncodeError:
                errors.append(f"{path}: invalid Unicode surrogate")
        elif item is None or type(item) is bool:
            continue
        elif type(item) is int:
            if item.bit_length() > 4096:
                errors.append(f"{path}: JSON integer size limit exceeded")
        elif type(item) is float:
            if not math.isfinite(item):
                errors.append(f"{path}: JSON numbers must be finite")
        elif isinstance(item, (list, dict)) and type(item) in (list, dict):
            if id(item) in parents:
                errors.append(f"{path}: circular JSON container")
                continue
            ancestry = parents | {id(item)}
            if len(item) > max_nodes - visited:
                errors.append(f"{path}: JSON node limit exceeded")
                continue
            if isinstance(item, list):
                pending.extend(
                    (child, f"{path}[{n}]", depth + 1, ancestry)
                    for n, child in reversed(list(enumerate(item)))
                )
            else:
                for key, child in reversed(list(item.items())):
                    if type(key) is not str:
                        errors.append(f"{path}: JSON object keys must be strings")
                        continue
                    pending.append((child, f"{path}[{key!r}]", depth + 1, ancestry))
                    pending.append((key, f"{path}.key", depth + 1, ancestry))
        else:
            errors.append(f"{path}: {type(item).__name__} is outside the JSON domain")
        if characters > max_characters:
            errors.append("JSON character limit exceeded")
            break
    return tuple(errors)
