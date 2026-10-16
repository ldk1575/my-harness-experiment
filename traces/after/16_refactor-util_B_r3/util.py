import re
from typing import Sequence, TypeVar, Union

T = TypeVar("T")
Number = Union[int, float]


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.

    Strips and lowercases the text, replaces every run of characters other
    than ASCII letters and digits with a single hyphen, and removes leading
    and trailing hyphens.

    Args:
        text: The input string.

    Returns:
        The slugified string (may be empty).
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def chunk(items: Sequence[T], size: int) -> list[Sequence[T]]:
    """Split a sequence into consecutive chunks of at most ``size`` items.

    Args:
        items: The sequence to split.
        size: Maximum number of items per chunk; must be positive.

    Returns:
        A list of slices of ``items``. The last chunk may be shorter.

    Raises:
        ValueError: If ``size`` is not positive.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items), size)]


def safe_div(a: Number, b: Number, default: Number = 0) -> Number:
    """Divide ``a`` by ``b``, returning ``default`` on division by zero.

    Args:
        a: The numerator.
        b: The denominator.
        default: Value returned when ``b`` is zero.

    Returns:
        The result of ``a / b``, or ``default`` if ``b`` is zero.
    """
    try:
        return a / b
    except ZeroDivisionError:
        return default
