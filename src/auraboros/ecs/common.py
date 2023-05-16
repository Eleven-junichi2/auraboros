from .component import Component
from .system import System

Velocity = Component("velocity", [0, 0])
Position = Component("position", [0, 0])
Size = Component("size", [1, 1])
HealthPoint = Component("health_point", 1)
ExperientPoint = Component("experient_point", 1)
Hp = HealthPoint
Exp = ExperientPoint


class MovementSystem(System):
    def do(self, *args, **kwargs):
        for entity in self.world.get_entities():
            self.world.edit_entity[entity]["position"].value = map(
                sum,
                zip(
                    self.world.component_for_entity(entity, "position"),
                    self.world.component_for_entity(entity, "velocity"),
                ),
            )
