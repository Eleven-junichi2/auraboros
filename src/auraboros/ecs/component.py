from dataclasses import dataclass
from typing import Generic, Self, TypeVar
import copy

_C = TypeVar("_C")


@dataclass
class Component(Generic[_C]):
    """Prototype(design pattern) class for components."""

    name: str
    _value: _C

    def __post_init__(self):
        self.__type_of_value = type(self.value)

    @property
    def value(self) -> _C:
        return self._value

    @value.setter
    def value(self, value: _C) -> None:
        if isinstance(value, self.__type_of_value):
            self._value = value
        else:
            try:
                # try casting value
                self._value = self.__type_of_value(value)
            except TypeError:
                raise TypeError(f"Type of value must be {self.__type_of_value}")

    def type_of_value(self) -> type[_C]:
        return self.__type_of_value

    def clone(self) -> Self:
        return copy.deepcopy(self)

    def new(self, value: _C):
        new_component = self.clone()
        new_component.value = value
        return new_component
