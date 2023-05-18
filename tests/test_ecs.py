from src.auraboros.ecs.world import World, System, component


def test_integration():
    @component
    class Position:
        x: int
        y: int

    @component
    class Velocity:
        x: int
        y: int

    @component
    class Weight:
        kg: float

    class Movement(System):
        def do(self):
            for entity in self.world.get_entities(Position, Velocity):
                self.world.component_for_entity(
                    entity, Position
                ).x += self.world.component_for_entity(entity, Velocity).x
                # `edit()` same as `component_for_entity()`
                self.world.edit(entity, Position).y += self.world.edit(
                    entity, Velocity
                ).y
                self.world.edit(entity, Weight).kg -= 0.1

    world = World()

    Ikuyo = world.create_entity(Weight(44), Velocity(194, 0), Position(1000, 30))
    Nijika = world.create_entity(Weight(48), Velocity(245, 0), Position(155, 30))
    Hitori = world.create_entity(Weight(50), Velocity(-20, 1), Position(0, 0))

    assert Ikuyo == 0
    assert Nijika == 1
    assert Hitori == 2

    world.add_system(Movement())
    world.do_systems()

    assert world.component_for_entity(Ikuyo, Weight).kg == 43.9
    assert world.component_for_entity(Hitori, Weight).kg == 49.9
    assert world.component_for_entity(Ikuyo, Position).x == 1194
    assert world.component_for_entity(Nijika, Position).x == 400
