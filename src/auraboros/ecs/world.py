from inspect import isclass
import logging

from .component import Component, CV
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


class _ComponentDict(dict[ComponentName, Component]):
    def __getitem__(self, __key):
        if isinstance(__key, Component):
            return super().__getitem__(__key.name)
        else:
            return super().__getitem__(__key)


class World:
    def __init__(self):
        self.next_entity_id: EntityID = 0
        self._entities: dict[EntityID, _ComponentDict[ComponentName, Component]] = {}
        self.systems: list[System] = []

    def get_entities(
        self, *of_has_components: Component, raise_error_if_not_found=True
    ):
        """
        Args:
            of_has_components: list of filter components to retrieve entities.
        """
        component_filter = [component.name for component in of_has_components]
        logger.debug(
            f"({self.get_entities.__name__}) given component filter: {component_filter}"
        )
        entities = []
        for entity in self._entities.keys():
            for component_name in self._entities[entity].keys():
                if component_name in component_filter:
                    entities.append(entity)
        if raise_error_if_not_found and entities == []:
            raise ValueError(
                f"No entities found with the specified components: {of_has_components}"
            )
        return entities

    def create_entity(self, *components: Component) -> EntityID:
        new_entity = self.next_entity_id
        self._entities[new_entity] = _ComponentDict()
        for component in components:
            if component.is_factory:
                raise ValueError(
                    "Given components contain factory.\nExample of this method: "
                    + f"{self.create_entity.__name__}(component_instance.new()"
                    + " # same as component_instance.be() ) "
                )
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
        if isclass(system_instance):
            raise ValueError("system_instance must be instance")
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

    def component_for_entity(
        self, entity: EntityID, component: Component[CV]
    ) -> Component[CV]:
        return self._entities[entity][component.name]
