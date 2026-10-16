import re
from typing import Sequence, TypeVar, Union

T = TypeVar("T")
Number = Union[int, float]


def slugify(text: str) -> str:
    """Convert text to a lowercase, hyphen-separated URL slug.

    Runs of characters other than ASCII letters and digits become a single
    hyphen, and leading/trailing hyphens are removed.
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def chunk(items: Sequence[T], size: int) -> list[Sequence[T]]:
    """Split items into consecutive slices of at most `size` elements.

    The last slice may be shorter. Raises ValueError if `size` is not positive.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items), size)]


def safe_div(a: Number, b: Number, default: Number = 0) -> Number:
    """Return a / b, or `default` if b is zero."""
    try:
        return a / b
    except ZeroDivisionError:
        return default
