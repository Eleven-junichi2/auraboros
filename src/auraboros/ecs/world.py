import logging

from .component import Component
from .system import System

# --setup logger--
logger = logging.getLogger(__name__)

log_format_str = "%(asctime)s [%(levelname)s]: %(message)s"
log_format_datefmt = "%Y-%m-%d %H:%M:%S"

# console
console_handler = logging.StreamHandler()
console_handler_formatter = logging.Formatter(log_format_str, log_format_datefmt)
console_handler.setFormatter(console_handler_formatter)
logger.addHandler(console_handler)
# ----

# --type aliases--
EntityID = int
ComponentName = str
# ----


class World:
    def __init__(self):
        self.next_entity_id: EntityID = 0
        self._entities: dict[EntityID, dict[ComponentName, Component]] = {}
        self.systems: list[System] = []

    def get_entities(self):
        return self._entities.keys()

    @property
    def edit_entity(self):
        """
        How to use:
        `self.edit_entities[entity_to_edit][component_name].value = something`
        """
        return self._entities

    def create_entity(self, *components_names: Component) -> EntityID:
        new_entity = self.next_entity_id
        self._entities[new_entity] = {}
        for component_factory in components_names:
            component = component_factory.clone()
            self._entities[new_entity][component.name] = component
        self.next_entity_id += 1
        logger.debug(f"create a entity (updated entities: {self._entities})")
        return new_entity

    def delete_entity(self, entity: EntityID) -> None:
        del self._entities[entity]

    def add_system(self, system_instance: System) -> None:
        """Add a system instance to the World.

        All systems should subclass of `System`.
        """
        system_instance.world = self
        self.systems.append(system_instance)
        logger.debug(f"add a system (updated systems: {self.systems})")

    def remove_system(self, system_type: type[System]) -> None:
        for index, system_instance in enumerate(self.systems):
            if isinstance(system_instance, system_type):
                logger.debug(f"remove {system_instance} system")
                del self.systems[index]
        logger.debug(f"systems after remove func: {self.systems})")

    def do_systems(self, *args, **kwargs) -> list:
        """Do all systems of the world and return a list of return values"""
        logger.debug(f"do all systems: {self.systems})")
        return [system.do(*args, **kwargs) for system in self.systems]

    def component_for_entity(self, entity: EntityID, component_name: str):
        return self._entities[entity][component_name].value
