import math
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Wall:
    """
    Orientation:
    0 goes from left to right.
    90 goes from top to bottom
    -180 goes from right to left
    -90 goes from bottom to top
    """

    length: float
    orientation: float


@dataclass
class WallSequence:
    walls: List[Wall]

    def as_points(self):
        points = [[0, 0]]
        for wall in self.walls:
            last_point = points[-1]
            rad = 2 * math.pi * wall.orientation / 360
            scale = 50
            length = scale * wall.length
            next_point = [
                last_point[0] + length * math.cos(rad),
                last_point[1] + length * math.sin(rad),
            ]
            points.append(next_point)

        return points


house = WallSequence(
    [
        Wall(4.25, 0),  # top left of bedroom
        Wall(3, 90),
        Wall(0.5, -180),  # door
        Wall(0.25, 0),
        Wall(2.5, 90),  # wall down
        Wall(2.5, -90),  # living room
        Wall(3, 0),
        Wall(4, 90),
        Wall(3, -180),
        Wall(0.5, -90),  # living room door
        Wall(2, 90),  # entrance
        Wall(1, -180),
        Wall(1.25, -90),
        Wall(1, 90),  # door bathroom
        Wall(3, -180),
        Wall(2, -90),
        Wall(3, 0),
        # door bathroom
        Wall(1.5, -90),
        Wall(0.5, 90),  # door kitchen
        Wall(3, -180),
        Wall(2, -90),
        Wall(3, 0),
        Wall(0.5, 90),
        Wall(0.75, -90),
        Wall(0.25, 0),
        Wall(3.25, -180),
    ]
)
