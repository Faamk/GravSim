from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from pygame.math import Vector2
import pygame
import math
import random
import string


@dataclass(eq=False)
class Entity(pygame.sprite.Sprite):
    position: Vector2
    old_position: Vector2
    collision_path : List[tuple[float,float]]
    density: float
    mass: float
    realRect: pygame.Rect
    velocity: float = 0
    direction: float = 0
    color: tuple = (255, 0, 0)
    draw_velocity: bool = False
    name: str = field(default_factory=lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=8)))

    def __init__(self, position: Vector2, density: float, mass: float,
                 velocity: float = 0, direction: float = 0,
                 color: tuple = (255, 0, 0), name: str = None, draw_velocity: bool = False):
        super().__init__()
        self.position = position
        self.old_position = position
        self.density = density
        self.mass = mass
        self.velocity = velocity
        self.direction = direction
        self.color = color
        self.name = name if name is not None else ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.image = None
        self.draw_velocity = draw_velocity
        self._update_real_rect()
        self.prev_rect = self.realRect
        self.collision_path = []

    def __getstate__(self) -> Dict:
        """Return a picklable state dictionary"""
        state = {
            'position': (self.position.x, self.position.y),
            'old_position': (self.old_position.x, self.old_position.y),
            'density': self.density,
            'mass': self.mass,
            'velocity': self.velocity,
            'direction': self.direction,
            'color': self.color,
            'draw_velocity': self.draw_velocity,
            'name': self.name,
            'rect': (self.realRect.x, self.realRect.y, self.realRect.width, self.realRect.height),
            'collision_path': self.collision_path,  # Store the collision_path as a list of points
        }
        return state

    def __setstate__(self, state: Dict) -> None:
        """Restore instance from pickled state"""
        # Initialize parent Sprite class
        pygame.sprite.Sprite.__init__(self)

        # Restore Vector2 position
        self.position = Vector2(*state['position'])
        self.old_position = Vector2(*state['old_position'])

        # Restore simple attributes
        self.density = state['density']
        self.mass = state['mass']
        self.velocity = state['velocity']
        self.direction = state['direction']
        self.color = state['color']
        self.draw_velocity = state['draw_velocity']
        self.name = state['name']

        # Restore Rect
        self.realRect = pygame.Rect(*state['rect'])

        # Restore the collision_path as a list of points
        self.collision_path = state['collision_path']

        # Recalculate the rectangle if necessary
        self._update_real_rect()

        # Initialize image as None (will be recreated when needed)
        self.image = None

    def __str__(self):
        return f"Entity '{self.name}'\n" \
               f"  Mass:    {self.mass:.2f} kg\n" \
               f"  Density: {self.density:.2f} kg/m³\n" \
               f"  Radius:  {self.radius:.2f} m"


    @property
    def radius(self) -> float:
        return math.sqrt(self.mass / (self.density * math.pi))

    def _update_real_rect(self) -> None:
        self.realRect = pygame.Rect(
            self.position.x - self.radius,
            self.position.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def move(self, x: float, y: float) -> None:
        self.old_position = deepcopy(self.position)
        self.position.x = x
        self.position.y = y
        self._update_real_rect()
        self.set_collision_path()
    def get_velocity_vector(self) -> Vector2:
        return Vector2(
            math.cos(self.direction) * self.velocity,
            math.sin(self.direction) * self.velocity
        )

    def consume(self, other: 'Entity') -> None:
        self.mass = self.mass + other.mass

    def set_collision_path(self) -> None:
        dx = self.position.x - self.old_position.x
        dy = self.position.y - self.old_position.y
        length = max(math.sqrt(dx ** 2 + dy ** 2), 0.001)

        dx /= length
        dy /= length

        # Perpendicular direction to the motion vector
        perp_dx = -dy
        perp_dy = dx

        # Scale the perpendicular vector by the radius
        perp_dx *= self.radius
        perp_dy *= self.radius

        # Define the four points that make up the collision path
        rect_start_1 = (self.old_position.x + perp_dx, self.old_position.y + perp_dy)
        rect_end_1 = (self.position.x + perp_dx, self.position.y + perp_dy)
        rect_start_2 = (self.old_position.x - perp_dx, self.old_position.y - perp_dy)
        rect_end_2 = (self.position.x - perp_dx, self.position.y - perp_dy)

        self.collision_path = [rect_start_1, rect_end_1, rect_end_2, rect_start_2]


