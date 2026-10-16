import re
from typing import Sequence, TypeVar, Union

T = TypeVar("T")
D = TypeVar("D")


def slugify(text: str) -> str:
    """Convert text to a lowercase, hyphen-separated URL slug.

    Leading/trailing whitespace is stripped, the text is lowercased, and every
    run of characters outside ``a-z0-9`` is replaced by a single hyphen.
    Leading and trailing hyphens are removed.

    Args:
        text: The text to convert.

    Returns:
        The slug; an empty string if no alphanumeric characters remain.
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def chunk(items: Sequence[T], size: int) -> list[Sequence[T]]:
    """Split a sequence into consecutive chunks of at most ``size`` items.

    Args:
        items: The sequence to split (must support ``len`` and slicing).
        size: Maximum number of items per chunk; must be positive.

    Returns:
        A list of slices of ``items``. The last chunk may be shorter than
        ``size``. An empty input yields an empty list.

    Raises:
        ValueError: If ``size`` is not positive.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items), size)]


def safe_div(a: float, b: float, default: D = 0) -> Union[float, D]:
    """Divide ``a`` by ``b``, returning ``default`` if ``b`` is zero.

    Args:
        a: The dividend.
        b: The divisor.
        default: Value returned when division by zero occurs. Defaults to 0.

    Returns:
        ``a / b``, or ``default`` when ``b`` is zero.
    """
    try:
        return a / b
    except ZeroDivisionError:
        return default
