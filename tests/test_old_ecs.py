import pytest

from src.auraboros.old_ecs.world import World
from src.auraboros.old_ecs.system import System
from src.auraboros.old_ecs.component import Component


def test_integration():
    Height = Component("height_cm", 160.0)
    Weight = Component("weight_kg", 50.0)
    IsMale = Component("is_male", True)
    SoccerPlayer = Component("soccer_player", True)
    world = World()
    Kita = world.create_entity(Height.be(158), Weight.be(44), IsMale.be(False))
    Gotou = world.create_entity(Height.be(156), Weight.be(50), IsMale.be(False))
    Naoki = world.create_entity(Height.be(None), Weight.be(None), IsMale.be(True))
    assert world.component_for_entity(Kita, Height).value == 158
    assert world.component_for_entity(Kita, Weight).value != 156
    assert world.component_for_entity(Gotou, Weight).value is not None
    assert world.component_for_entity(Naoki, IsMale).value

    class GoJogging(System):
        def do(self, *args, **kwargs):
            for entity in self.world.get_entities(Weight):
                self.world.component_for_entity(entity, Weight).value -= 2

    class Sleep(System):
        def do(self, *args, **kwargs):
            for entity in self.world.get_entities(Height):
                self.world.component_for_entity(entity, Height).value += 0.5

    class ToBeFaliedSystem(System):
        def do(self, *args, **kwargs):
            for entity in self.world.get_entities(SoccerPlayer):
                self.world.component_for_entity(entity, SoccerPlayer).value

    with pytest.raises(ValueError):
        world.add_system(GoJogging)
    world.add_system(GoJogging())
    world.add_system(Sleep())
    world.do_systems()

    assert world.component_for_entity(Kita, Weight).value == 42
    assert world.component_for_entity(Gotou, Height).value == 156.5

    world.add_system(ToBeFaliedSystem())
    with pytest.raises(ValueError):
        world.do_systems()

    world.remove_system(ToBeFaliedSystem)
    assert not all([isinstance(system, ToBeFaliedSystem) for system in world.systems])
