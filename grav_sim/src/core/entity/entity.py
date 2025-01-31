from dataclasses import dataclass
from typing import List

from pygame.math import Vector2
import pygame
import math


@dataclass(eq=False)
class Entity(pygame.sprite.Sprite):
    position: Vector2
    density: float
    mass: float
    velocity: float = 0
    direction: float = 0
    color: tuple = (255, 0, 0)

    def __init__(self, position: Vector2, density: float, mass: float,
                 velocity: float = 0, direction: float = 0,
                 color: tuple = (255, 0, 0)):
        super().__init__()
        self.position = position
        self.density = density
        self.mass = mass
        self.velocity = velocity
        self.direction = direction
        self.color = color
        self.image = None

    @property
    def radius(self) -> float:
        return math.sqrt(self.mass / (self.density * math.pi))

    def check_collisions(self, entities: List['Entity']) -> None:
        for other in entities[:]:  # Create a copy of list to safely modify it
            if other is self:
                continue

            if not self.collide(other):
                continue

            if self.mass >= other.mass:
                self.consume(other)
                entities.remove(other)

    def collide(self, other: 'Entity') -> bool:
        """Check if this entity collides with another entity"""
        distance = (self.position - other.position).length()
        return distance < (self.radius + other.radius)

    def move(self, time_scale: float):
        movement = Vector2(
            math.cos(self.direction) * self.velocity * time_scale,
            math.sin(self.direction) * self.velocity * time_scale
        )
        self.position += movement

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
