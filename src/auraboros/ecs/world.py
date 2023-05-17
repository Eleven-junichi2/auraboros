from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from inspect import isclass
from typing import Iterable, Optional, Self, TypeVar, Generic, ClassVar
import logging

CV = TypeVar("CV")

# --setup logger--
logger = logging.getLogger(__name__)

log_format_str = "%(levelname)s - %(message)s"
log_format_datefmt = "%Y-%m-%d %H:%M:%S"

# console
console_handler = logging.StreamHandler()
console_handler_formatter = logging.Formatter(log_format_str, log_format_datefmt)
console_handler.setFormatter(console_handler_formatter)
logger.addHandler(console_handler)
# ----

# -type aliases-
EntityID = int
ComponentID = int
ArchetypeID = int
CarrierID = int
# ArchetypeMap = dict[ArchetypeID: Component]
Type = list[ComponentID]
# ---


@dataclass
class Component(Generic[CV]):
    next_id: ClassVar[ComponentID] = 0
    _type: type[CV]
    _default_value: Optional[CV] = None

    def __post_init__(self):
        self.id = Component.next_id
        Component.next_id += 1

    def __call__(self, default_value: CV) -> Self:
        self.default_value = default_value
        return self

    @property
    def type(self) -> type[CV]:
        return self._type

    @property
    def default_value(self) -> CV:
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self.cast_value_if_invalid_type(value)

    def cast_value_if_invalid_type(self, value):
        if not isinstance(value, self.type) and value is not None:
            try:
                logger.debug(
                    f"try cast given {value} to {self.type} type"
                    + " as default value of component"
                )
                value = self.type(value)
            except TypeError:
                raise TypeError(f"Type of value must be {self.type}")
        self._default_value = value


class System(metaclass=ABCMeta):
    world: "World"

    @abstractmethod
    def do(self):
        raise NotImplementedError


class World:
    """
    Type Aliases:
        EntityID = int:
        ComponentID = tnt:
    """

    def __init__(self):
        self.next_entity_id: EntityID = 0
        self._entities: dict[EntityID, set[ComponentID]] = {}
        self.components: dict[ComponentID, dict[EntityID, CV]] = {}
        self._types_for_components: dict[ComponentID, type[CV]] = {}
        self._systems: list[System] = []

    def create_entity(self, *components: Component[CV]) -> EntityID:
        """
        #----
             id   weig          heig        gend        teac
        enti 0000   01 int 0150 0150 int 02 true bol 01 true bol 02
        enti 0001   02 int 0160 0160 int 03 fals bol 03 None
        enti 0002 None          0180 int 04 true bol 04

        self.component_types:
        weig: (cmpnnt_id: 01)
             value_id value
                    1   150
                    2   160
        heig: (cmpnnt_id: 02)
             value_id  value
                    1   50
                    2   60
        #----
        """
        new_entity = self.next_entity_id
        self._entities[new_entity] = set()
        for component in components:
            logger.debug(
                "load component:\n\t"
                + f"type: {component.type} default_value: {component.default_value}"
            )
            if component.id not in self.components.keys():
                self.components[component.id] = {}
            self.components[component.id][new_entity] = component.default_value
            self._types_for_components[component.id] = component.type
            self._entities[new_entity].add(component.id)
        logger.debug(f"result of entity(id:{new_entity}) creation:")
        logger.debug(f"updated entities:\n\t\t{self._entities}")
        logger.debug(f"updated components:\n\t\t{self.components}")
        self.next_entity_id += 1
        return new_entity

    def delete_entity(self, entity: EntityID) -> None:
        del self._entities[entity]
        [
            self.components[component].__delitem__(entity)
            for component in self.components.keys()
            if entity in self.components[component].keys()
        ]
        del entity

    def get_entities(self, *components: Component) -> Iterable[EntityID]:
        return (
            entity
            for entity in self._entities.keys()
            if self._entities[entity].intersection(
                set([component.id for component in components])
            )
        )

    def add_system(self, system: System):
        if isclass(system):
            raise ValueError("system_instance must be instance")
        system.world = self
        self._systems.append(system)

    def remove_system(self, system_type: type[System]) -> None:
        if not isclass(system_type):
            raise ValueError("system_type must be the class")
        else:
            [
                self._systems.remove(system)
                for system in self._systems
                if isinstance(system, system_type)
            ]

    def do_systems(self):
        logger.debug(f"do all systems of {self}")
        [system.do() for system in self._systems]
