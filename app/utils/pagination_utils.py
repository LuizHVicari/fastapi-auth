from ast import TypeVar
from dataclasses import dataclass

T = TypeVar("T")


@dataclass(kw_only=True, frozen=True, slots=True)
class Paginated[T]:
    items: tuple[T, ...]
    total: int
