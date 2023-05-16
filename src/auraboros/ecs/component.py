from dataclasses import dataclass
from typing import Generic, Optional, Self, TypeVar
import copy

CV = TypeVar("CV")


@dataclass
class Component(Generic[CV]):
    """Prototype(design pattern) class for components."""

    name: str
    _value: CV
    type_of_value: Optional[type[CV]] = None
    is_factory: bool = True

    def __post_init__(self):
        if self.type_of_value is None:
            self.type_of_value = type(self._value)

    @property
    def value(self) -> CV:
        return self._value

    @value.setter
    def value(self, value: CV) -> None:
        if isinstance(value, (self.type_of_value)) or value is None:
            self._value = value
        else:
            try:
                # try casting value
                self._value = self.type_of_value(value)
            except TypeError:
                raise TypeError(f"Type of value must be {self.type_of_value}")

    def _clone(self) -> Self:
        return copy.deepcopy(self)

    def new(self, value: Optional[CV]):
        new_component = self._clone()
        new_component.is_factory = False
        if value:
            new_component.value = value
        return new_component

    be = new  # alias of method
