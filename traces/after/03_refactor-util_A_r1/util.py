import re
from typing import Any, Sequence


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.

    Lowercases the text, replaces each run of characters outside
    ``a-z0-9`` with a single hyphen, and strips leading/trailing hyphens.

    Args:
        text: The string to convert.

    Returns:
        The slugified string (empty if no alphanumeric characters remain).
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def chunk(items: Sequence[Any], size: int) -> list[Sequence[Any]]:
    """Split a sequence into consecutive chunks of at most ``size`` items.

    Args:
        items: The sequence to split (must support slicing and ``len``).
        size: Maximum length of each chunk; must be positive.

    Returns:
        A list of slices of ``items``; the last one may be shorter.

    Raises:
        ValueError: If ``size`` is not positive.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items), size)]


def safe_div(a: float, b: float, default: float = 0) -> float:
    """Divide ``a`` by ``b``, returning ``default`` on division by zero.

    Args:
        a: The numerator.
        b: The denominator.
        default: Value returned when ``b`` is zero.

    Returns:
        ``a / b``, or ``default`` if ``b`` is zero.
    """
    try:
        return a / b
    except ZeroDivisionError:
        return default
