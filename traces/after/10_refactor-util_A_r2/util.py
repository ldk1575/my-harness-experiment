import re
from typing import Sequence, TypeVar

T = TypeVar("T")


def slugify(text: str) -> str:
    """Convert text to a lowercase, hyphen-separated URL slug.

    Leading/trailing whitespace is stripped, and every run of characters
    other than ASCII letters and digits becomes a single hyphen. Hyphens at
    the ends of the result are removed.

    Args:
        text: The string to convert.

    Returns:
        The slug, which may be empty if text has no alphanumeric characters.
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def chunk(items: Sequence[T], size: int) -> list[Sequence[T]]:
    """Split a sequence into consecutive chunks of at most ``size`` items.

    Args:
        items: The sequence to split. Must support slicing and len().
        size: Maximum number of items per chunk. Must be positive.

    Returns:
        A list of slices of ``items``. The last chunk may be shorter than
        ``size``. An empty input yields an empty list.

    Raises:
        ValueError: If size is not positive.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items), size)]


def safe_div(a: float, b: float, default: float = 0) -> float:
    """Divide a by b, returning a default value when b is zero.

    Args:
        a: The numerator.
        b: The denominator.
        default: Value returned if the division raises ZeroDivisionError.

    Returns:
        The result of ``a / b``, or ``default`` if b is zero.
    """
    try:
        return a / b
    except ZeroDivisionError:
        return default
