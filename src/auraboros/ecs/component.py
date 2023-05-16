from dataclasses import dataclass
from typing import Generic, Optional, Self, TypeVar
import copy

_Any = TypeVar("_Any")


@dataclass
class Component(Generic[_Any]):
    """Prototype(design pattern) class for components."""

    name: str
    _value: _Any
    is_factory: bool = True

    def __post_init__(self):
        self.__type_of_value = type(self.value)

    @property
    def value(self) -> _Any:
        return self._value

    @value.setter
    def value(self, value: _Any) -> None:
        if isinstance(value, (self.__type_of_value)) or value is None:
            self._value = value
        else:
            try:
                # try casting value
                self._value = self.__type_of_value(value)
            except TypeError:
                raise TypeError(f"Type of value must be {self.__type_of_value}")

    def type_of_value(self) -> type[_Any]:
        return self.__type_of_value

    def _clone(self) -> Self:
        return copy.deepcopy(self)

    def new(self, value: Optional[_Any]):
        new_component = self._clone()
        new_component.is_factory = False
        if value:
            new_component.value = value
        return new_component

    be = new  # alias of method
