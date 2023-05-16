import pytest

from src.auraboros.ecs.world import World
from src.auraboros.ecs.system import System
from src.auraboros.ecs.component import Component


class TestComponent:
    def test_integration(self):
        Height = Component("height_cm", 160.)
        Weight = Component("weight_kg", 50.)
        IsMale = Component("is_male", True)
        world = World()
        Kita = world.create_entity(Height.be(158), Weight.be(44), IsMale.be(False))
        Gotou = world.create_entity(Height.be(156), Weight.be(50), IsMale.be(False))
        Naoki = world.create_entity(Height.be(None), Weight.be(None), IsMale.be(True))
        assert world.component_for_entity(Kita, Height) == 158
        assert world.component_for_entity(Kita, Weight) != 156
        assert world.component_for_entity(Gotou, Weight) is not None
        assert world.component_for_entity(Naoki, IsMale)

        class GoJogging(System):
            def do(self, *args, **kwargs):
                for entity in self.world.get_entities():
                    self.world.edit_entity[entity][Weight].value -= 2

        class Sleep(System):
            def do(self, *args, **kwargs):
                for entity in self.world.get_entities():
                    self.world.edit_entity[entity][Height].value += 0.5

        with pytest.raises(ValueError):
            world.add_system(GoJogging)
        world.add_system(GoJogging())
        world.add_system(Sleep())
        world.do_systems()

        assert world.component_for_entity(Kita, Weight) == 42
        assert world.component_for_entity(Gotou, Height) == 156.5
