# import pytest

from src.auraboros.ecs.world import World, Component, System


def test_integration():
    world = World()
    Height = Component(float)
    assert Height.id == 0
    assert Height.default_value is None
    Weight = Component(float)
    assert Weight.id == 1
    ikuyo = world.create_entity(Height(158), Weight(44))
    assert ikuyo == 0
    hitori = world.create_entity(Height(156), Weight(50))
    assert hitori == 1
    assert (ikuyo and hitori) in world.get_entities(Height)
    assert (ikuyo and hitori) in world.get_entities(Weight)

    class SleepSystem(System):
        def do(self):
            for entity in world.get_entities(Height):
                world.components[Height.id][entity] += 0.3

    world.add_system(SleepSystem())
    world.do_systems()

    assert world.components[Height.id][ikuyo] == 158.3
    assert world.components[Height.id][hitori] == 156.3

    world.remove_system(SleepSystem)
    assert not world._systems

    world.delete_entity(ikuyo)
    assert ikuyo not in world.get_entities(Height)
    assert ikuyo not in world._entities.keys()
