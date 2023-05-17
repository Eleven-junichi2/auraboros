import logging

import setup_syspath  # noqa
from ecs.common import Velocity, Position, MovementSystem
from ecs.world import World
from ecs.world import logger as world_logger

world_logger.setLevel(logging.DEBUG)


world = World()

player = world.create_entity(Velocity.new([10, 10]), Position.new([10, 10]))

world.add_system(MovementSystem())

world_logger.info(
    f"Position of player: {world.component_for_entity(player, Position.name)}",
)

world.do_systems()

world_logger.info(
    f"Position of player: {world.component_for_entity(player, Position.name)}",
)

world.remove_system(MovementSystem)
