from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World


class System:
    world: "World"

    def do(self, *args, **kwargs):
        raise NotImplementedError
