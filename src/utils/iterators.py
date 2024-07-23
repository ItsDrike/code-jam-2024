from collections.abc import Iterator


def get_first[T](it: Iterator[T]) -> T | None:
    """Get the first item from an iterable, or None if it's empty."""
    try:
        return next(it)
    except StopIteration:
        return None
