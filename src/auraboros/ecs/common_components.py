from dataclasses import dataclass as component
from dataclasses import field


@component
class Position:
    pos: list[int] = field(default_factory=lambda: [0, 0])


@component
class Size:
    size: list[int] = field(default_factory=lambda: [0, 0])


@component
class Velocity:
    x: float = 0
    y: float = 0
