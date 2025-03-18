from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

from pygame import Rect, Vector2
from pygame.math import Vector2
import pygame
import math
import random
import string


@dataclass(eq=False)
class Entity(pygame.sprite.Sprite):
    position: Vector2
    old_position: Vector2
    density: float
    mass: float
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

    def __getstate__(self) -> Dict:
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
        }
        return state

    def __setstate__(self, state: Dict) -> None:
        pygame.sprite.Sprite.__init__(self)

        self.position = Vector2(*state['position'])
        self.old_position = Vector2(*state['old_position'])

        self.density = state['density']
        self.mass = state['mass']
        self.velocity = state['velocity']
        self.direction = state['direction']
        self.color = state['color']
        self.draw_velocity = state['draw_velocity']
        self.name = state['name']
        self.image = None

    def __str__(self):
        return f"Entity '{self.name}'\n" \
               f"  Mass:    {self.mass:.2f} kg\n" \
               f"  Density: {self.density:.2f} kg/m³\n" \
               f"  Radius:  {self.radius:.2f} m"


    @property
    def radius(self) -> float:
        return math.sqrt(self.mass / (self.density * math.pi))

    @property
    def realRect(self) -> Rect:
        return pygame.Rect(
            self.position.x - self.radius,
            self.position.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    @property
    def oldRect(self) -> Rect:
        return pygame.Rect(
            self.old_position.x - self.radius,
            self.old_position.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    @property
    def collision_path(self) -> list[Vector2]:
        displacement = self.position - self.old_position
        length = max(displacement.length(), 0.001)
        direction = displacement / length

        perp_direction = Vector2(-direction.y, direction.x)
        perp_direction *= self.radius * 2

        start_offset = self.old_position + perp_direction
        end_offset = self.position + perp_direction
        start_neg_offset = self.old_position - perp_direction
        end_neg_offset = self.position - perp_direction

        return [start_offset, end_offset, end_neg_offset, start_neg_offset]

    @property
    def collision_mask(self) -> pygame.Surface:
        # Create a surface to draw the collision mask
        mask_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        # Draw a circle for the current position (centered at self.position)
        pygame.draw.circle(mask_surface, self.color,
                           (self.position.x - self.position.x + self.radius,
                            self.position.y - self.position.y + self.radius),
                           self.radius)

        # Draw a circle for the old position (centered at self.old_position)
        pygame.draw.circle(mask_surface, self.color,
                           (self.old_position.x - self.old_position.x + self.radius,
                            self.old_position.y - self.old_position.y + self.radius),
                           self.radius)

        # Draw the path of movement (collision path) as an outline
        path_points = self.collision_path
        pygame.draw.polygon(mask_surface, self.color, path_points, 1)

        return mask_surface

    def move(self, x: float, y: float) -> None:
        self.old_position = deepcopy(self.position)
        self.position.x = x
        self.position.y = y

    def get_velocity_vector(self) -> Vector2:
        return Vector2(
            math.cos(self.direction) * self.velocity,
            math.sin(self.direction) * self.velocity
        )

    def consume(self, other: 'Entity') -> None:
        self.mass = self.mass + other.mass

    def draw(self, canvas, camera, show_old):
        screen_size = camera.world_to_screen_radius(self.radius)
        screen_position = camera.world_to_screen_pos(self.position)

        if show_old:
            pygame.draw.circle(canvas, self.color,  camera.world_to_screen_pos(self.old_position), screen_size, 1)
            path_points = [camera.world_to_screen_pos(point) for point in self.collision_path]
            pygame.draw.polygon(canvas, self.color, path_points, 1),

        if screen_size == 1:
            canvas.set_at((round(screen_position.x), round(screen_position.y)), self.color)
        else:
            pygame.draw.circle(canvas, self.color, screen_position, screen_size)


