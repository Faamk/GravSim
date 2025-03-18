import math
import random
from pygame.math import Vector2
from grav_sim.src.config.settings import PhysicsConfig, BoardConfig
from grav_sim.src.core.entity.entity import Entity
from typing import List


def create_entity_orbit_at_radius(name: str, orbit_radius: float, mass: float, color: tuple, central_body: Entity) -> Entity:
    angle_offset = random.uniform(0, 2 * math.pi)

    pos = Vector2(
        central_body.position.x + orbit_radius * math.cos(angle_offset),
        central_body.position.y + orbit_radius * math.sin(angle_offset)
    )

    orbital_velocity = math.sqrt(
        (PhysicsConfig.GRAVITY_CONSTANT * central_body.mass) / orbit_radius
    ) * 0.7

    parent_velocity = Vector2(
        math.cos(central_body.direction) * central_body.velocity,
        math.sin(central_body.direction) * central_body.velocity
    )

    orbital_velocity_vector = Vector2(-math.sin(angle_offset), math.cos(angle_offset)) * orbital_velocity
    total_velocity_vector = orbital_velocity_vector + parent_velocity

    final_velocity = total_velocity_vector.length()
    final_direction = math.atan2(total_velocity_vector.y, total_velocity_vector.x)

    return Entity(
        name=name,
        position=pos,
        density=0.141,
        mass=mass,
        velocity=final_velocity,
        direction=final_direction,
        color=color
    )

def create_default_entities() -> List[Entity]:
    sun = Entity(
        name="Sun",
        position=Vector2(BoardConfig.WIDTH / 2, BoardConfig.HEIGHT / 2),
        density=0.141,
        mass=33300,
        velocity=0.0,
        direction=0,
        color=(255, 215, 0)
    )

    earth = create_entity_orbit_at_radius(
        name="Urath",
        orbit_radius=40000,  # Average Earth-Sun distance scaled down
        mass=1000,
        color=(0, 0, 255),
        central_body=sun
    )

    moon = create_entity_orbit_at_radius(
        name="Woon",
        orbit_radius=2000,  # Average Moon-Earth distance scaled down
        mass=12,  # Moon's mass is about 1.2% of Earth's mass
        color=(200, 200, 200),
        central_body=earth
    )

    return [sun, earth, moon]


def create_random_entities(num_entities: int, max_mass: float = 1000, max_velocity: float = 10) -> List[Entity]:
    entities = []

    sun = Entity(
        name="Sun",
        position=Vector2(BoardConfig.WIDTH / 2, BoardConfig.HEIGHT / 2),
        density=0.141,
        mass=333000,
        velocity=0.0,
        direction=0,
        color=(255, 215, 0)
    )

    entities.append(sun),

    for i in range(num_entities - 1):
        orbit_radius = random.uniform(10000, 80000)  # Random orbital radius

        mass = random.uniform(10, max_mass)

        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

        entities.append(create_entity_orbit_at_radius(
            name=f"Entity_{i}",
            orbit_radius=orbit_radius,
            mass=mass,
            color=color,
            central_body=sun
        ))

    return entities

def create_collision_test_entities() -> List[Entity]:
    # Create a very dense sun-like entity in the center
    sun = Entity(
        name="Sun",
        position=Vector2(BoardConfig.WIDTH / 2, BoardConfig.HEIGHT / 2),
        density=0.141,
        mass=100000,
        velocity=0.0,
        direction=0,
        color=(255, 215, 0)
    )

    # Create three close orbiting entities with very large masses
    entity_1 = create_entity_orbit_at_radius(
        name="Entity_1",
        orbit_radius=2000,  # Extremely close orbit
        mass=1000,
        color=(255, 0, 0),  # Red
        central_body=sun
    )

    entity_2 = create_entity_orbit_at_radius(
        name="Entity_2",
        orbit_radius=2500,  # Extremely close orbit
        mass=1000,
        color=(0, 255, 0),  # Green
        central_body=sun
    )

    entity_3 = create_entity_orbit_at_radius(
        name="Entity_3",
        orbit_radius=3000,  # Extremely close orbit
        mass=1000,
        color=(0, 0, 255),  # Blue
        central_body=sun
    )

    # Return the entities as a list
    return [sun, entity_1, entity_2, entity_3]