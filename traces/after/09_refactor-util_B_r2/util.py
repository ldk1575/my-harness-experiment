import re
from typing import Sequence, TypeVar

T = TypeVar("T")


def slugify(text: str) -> str:
    """Convert text to a lowercase, hyphen-separated slug.

    Leading/trailing whitespace is stripped, and every run of characters
    other than ASCII letters and digits becomes a single hyphen. Hyphens
    at the ends of the result are removed.
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def chunk(items: Sequence[T], size: int) -> list[Sequence[T]]:
    """Split a sequence into consecutive chunks of at most ``size`` items.

    The last chunk may be shorter. Each chunk is a slice of ``items``, so
    it has the same sequence type as the input.

    Raises:
        ValueError: If ``size`` is not positive.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items), size)]


def safe_div(a: float, b: float, default: float = 0) -> float:
    """Divide ``a`` by ``b``, returning ``default`` if ``b`` is zero."""
    try:
        return a / b
    except ZeroDivisionError:
        return default
