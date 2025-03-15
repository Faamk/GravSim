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
        self.density = density
        self.mass = mass
        self.velocity = velocity
        self.direction = direction
        self.color = color
        self.name = name if name is not None else ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.image = None
        self.draw_velocity = draw_velocity
        self._update_real_rect()

    def __getstate__(self) -> Dict:
        """Return a picklable state dictionary"""
        state = {
            'position': (self.position.x, self.position.y),
            'density': self.density,
            'mass': self.mass,
            'velocity': self.velocity,
            'direction': self.direction,
            'color': self.color,
            'draw_velocity': self.draw_velocity,
            'name': self.name,
            'rect': (self.realRect.x, self.realRect.y, self.realRect.width, self.realRect.height)
        }
        return state

    def __setstate__(self, state: Dict) -> None:
        """Restore instance from pickled state"""
        # Initialize parent Sprite class
        pygame.sprite.Sprite.__init__(self)

        # Restore Vector2 position
        self.position = Vector2(*state['position'])

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
        self.position.x = x
        self.position.y = y
        self._update_real_rect()

    def get_velocity_vector(self) -> Vector2:
        return Vector2(
            math.cos(self.direction) * self.velocity,
            math.sin(self.direction) * self.velocity
        )

    def consume(self, other: 'Entity') -> None:
        old_mass = self.mass
        self.mass += other.mass

        self_momentum = self.get_velocity_vector() * old_mass
        other_momentum = other.get_velocity_vector() * other.mass
        total_momentum = self_momentum + other_momentum

        self.velocity = total_momentum.length() / self.mass
        self.direction = math.atan2(total_momentum.y, total_momentum.x)
