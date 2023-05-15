from dataclasses import dataclass, field, asdict


@dataclass
class Arrow:
    """Arrow symbol"""

    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3


@dataclass
class ArrowToTurnToward:
    """Use to set direction"""

    is_up: bool = field(default=False)
    is_down: bool = field(default=False)
    is_right: bool = field(default=False)
    is_left: bool = field(default=False)

    def set(self, direction: Arrow):
        if direction is Arrow.UP:
            self.is_up = True
        elif direction is Arrow.DOWN:
            self.is_down = True
        elif direction is Arrow.RIGHT:
            self.is_right = True
        elif direction is Arrow.LEFT:
            self.is_left = True

    def unset(self, direction: Arrow):
        if direction is Arrow.UP:
            self.is_up = False
        elif direction is Arrow.DOWN:
            self.is_down = False
        elif direction is Arrow.RIGHT:
            self.is_right = False
        elif direction is Arrow.LEFT:
            self.is_left = False

    def is_set_any(self):
        return True in set(asdict(self).values())
