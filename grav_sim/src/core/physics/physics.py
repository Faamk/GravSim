import math
from typing import List
from pygame.math import Vector2
from grav_sim.src.config.settings import PhysicsConfig, BoardConfig
from grav_sim.src.core.entity.entity import Entity


def _check_collision(entity1: Entity, entity2: Entity) -> bool:
    distance = (entity1.position - entity2.position).length()
    return distance < (entity1.radius + entity2.radius)


def _get_velocity_vector(entity: Entity) -> Vector2:
    return Vector2(
        math.cos(entity.direction) * entity.velocity,
        math.sin(entity.direction) * entity.velocity
    )


class PhysicsEngine:
    def __init__(self, entities: List[Entity]):
        self.entities = entities

    def update(self, time_scale: float) -> None:
        for entity in self.entities:
            self._update_entity(entity, time_scale)

    def _update_entity(self, entity: Entity, time_scale: float) -> None:
        velocity_vector = _get_velocity_vector(entity)
        gravity_vector = self._calculate_gravity_vector(entity, time_scale)

        new_velocity = velocity_vector + gravity_vector
        entity.velocity = new_velocity.length()
        entity.direction = math.atan2(new_velocity.y, new_velocity.x)

        entity.move(time_scale)
        self._handle_collisions(entity)

    def _calculate_gravity_vector(self, entity: Entity, time_scale: float) -> Vector2:
        G = PhysicsConfig.GRAVITY_CONSTANT * time_scale
        gravity_vector = Vector2(0, 0)

        for other in self.entities:
            if other is entity:
                continue

            direction = other.position - entity.position
            distance = direction.length()
            if distance == 0:
                continue

            force = G * entity.mass * other.mass / (distance * distance)
            acceleration = force / entity.mass
            gravity_vector += direction.normalize() * acceleration

        return gravity_vector

    def _handle_collisions(self, entity: Entity) -> None:
        self._handle_entity_collisions(entity)

    def _handle_entity_collisions(self, entity: Entity) -> None:
        for other in self.entities[:]:
            if other is entity:
                continue

            if not entity.collide(other):
                continue

            if entity.mass >= other.mass:
                entity.consume(other)
                self.entities.remove(other)

    def _merge_entities(self, entity: Entity, other: Entity) -> None:
        self.entities.remove(other)
        old_mass = entity.mass
        entity.mass += other.mass

        entity_momentum = _get_velocity_vector(entity) * old_mass
        other_momentum = _get_velocity_vector(other) * other.mass
        total_momentum = entity_momentum + other_momentum

        entity.velocity = total_momentum.length() / entity.mass
        entity.direction = math.atan2(total_momentum.y, total_momentum.x)