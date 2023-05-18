from abc import ABCMeta, abstractmethod
from dataclasses import dataclass as component  # noqa
from inspect import isclass
from typing import Iterable, TypeVar
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
        self._entities: dict[EntityID, set[type[CV]]] = {}
        self._components: dict[type[CV], dict[EntityID, CV]] = {}
        self._systems: list[System] = []

    def create_entity(self, *components) -> EntityID:
        new_entity = self.next_entity_id
        self._entities[new_entity] = set()
        for component_ in components:
            logger.debug(
                "load component:\n\t" + f"{component_}(type: {component_.__class__})"
            )
            if type(component_) not in self._components.keys():
                self._components[type(component_)] = {}
            self._components[type(component_)][new_entity] = component_
            self._entities[new_entity].add(type(component_))
        logger.debug(f"result of entity(id:{new_entity}) creation:")
        logger.debug(f"updated entities:\n\t\t{self._entities}")
        logger.debug(f"updated components:\n\t\t{self._components}")
        self.next_entity_id += 1
        return new_entity

    def delete_entity(self, entity: EntityID) -> None:
        del self._entities[entity]
        [
            self._components[component].__delitem__(entity)
            for component_ in self._components.keys()
            if entity in self._components[component_].keys()
        ]
        del entity

    def get_entities(self, *components: type) -> Iterable[EntityID]:
        return (
            entity
            for entity in self._entities.keys()
            if self._entities[entity].intersection(
                set([component_ for component_ in components])
            )
        )

    def component_for_entity(self, entity: EntityID, component: type[CV]) -> CV:
        """Get the component for a given entity.
        `edit()` is alias for this method.
        """
        return self._components[component][entity]

    edit = component_for_entity  # alias for component_for_entity

    def add_system(self, system: System):
        if isclass(system):
            raise ValueError("system must be instance")
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
