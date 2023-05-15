from typing import Any, Iterable, TypeVar
from pprint import pformat
import logging


from .system import System

# --logger configuration--
logger = logging.getLogger(__name__)

log_format_str = "%(asctime)s [%(levelname)s]: %(message)s"
log_format_datefmt = "%Y-%m-%d %H:%M:%S"

# console
console_handler = logging.StreamHandler()
console_handler_formatter = logging.Formatter(log_format_str, log_format_datefmt)
console_handler.setFormatter(console_handler_formatter)
logger.addHandler(console_handler)
# ----

C = TypeVar("C")  # C means Component instance
C2 = TypeVar("C2")

EntityID = int  # type alias


class World:
    def __init__(self):
        self._next_entity_id = 0
        self.entities: dict[EntityID, dict] = {}
        self.components: dict[type, set] = {}
        self.systems: list[System] = []

    def create_entity(self, *component_instances) -> EntityID:
        new_entity_id = self._next_entity_id
        self.__add_new_entity(new_entity_id)

        for component in component_instances:
            component_type = type(component)
            if component_type not in self.components:
                self.components[component_type] = set()
            self.components[component_type].add(new_entity_id)

            self.entities[new_entity_id][component_type] = component

        logger.debug(
            f"update entities of {id(self)} {self.__class__.__name__} instance:\n"
            + pformat(self.entities)
        )

        return new_entity_id

    def get_component(self, component_type: type[C]) -> Iterable[tuple[EntityID, C]]:
        for entity in self.components.get(component_type, ()):
            yield entity, self.entities[entity][component_type]

    def get_components(
        self, *component_types: type[C]
    ) -> Iterable[tuple[EntityID, tuple[C, ...]]]:
        for entity in set.intersection(
            *[self.components[component_type] for component_type in component_types]
        ):
            yield entity, tuple(
                [
                    self.entities[entity][component_type]
                    for component_type in component_types
                ]
            )

    def component_for_entity(self, entity: int, component_type: type[C]) -> C:
        return self.entities[entity][component_type]

    def add_system(self, system_instance: System) -> None:
        """Add a system instance to the World.

        All systems should subclass of `System`.
        """
        system_instance.world = self
        self.systems.append(system_instance)

        logger.debug(
            f"update systems of {id(self)} {self.__class__.__name__} instance:\n"
            + pformat(self.systems)
        )

    def do_systems(self, *args, **kwargs) -> list[Any]:
        """Do all systems of the world and return a list of return values"""
        return [system.do(*args, **kwargs) for system in self.systems]

    def __add_new_entity(self, new_entity_id):
        if new_entity_id not in self.entities:
            self.entities[new_entity_id] = {}
