import math
import random
from pygame.math import Vector2
from grav_sim.src.config.settings import PhysicsConfig, BoardConfig
from grav_sim.src.core.entity.entity import Entity
from typing import List


def create_entity_orbit_at_radius(name: str, orbit_radius: float, mass: float, color: tuple,
                                  central_body: Entity) -> Entity:
    pos = Vector2(
        central_body.position.x + orbit_radius,
        central_body.position.y
    )

    orbital_velocity = math.sqrt(
        (PhysicsConfig.GRAVITY_CONSTANT * central_body.mass) / orbit_radius
    ) * 0.7

    parent_velocity = Vector2(
        math.cos(central_body.direction) * central_body.velocity,
        math.sin(central_body.direction) * central_body.velocity
    )

    orbital_velocity_vector = Vector2(0, orbital_velocity)
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
    
    # Create random entities
    for i in range(num_entities - 1):
        # Random position across the board
        pos = Vector2(
            random.uniform(0, BoardConfig.WIDTH),
            random.uniform(0, BoardConfig.HEIGHT)
        )
        
        # Random RGB color
        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        
        entities.append(Entity(
            name=f"Entity_{i}",
            position=pos,
            density=0.141,
            mass=random.uniform(10, max_mass),
            velocity=random.uniform(0, max_velocity),
            direction=random.uniform(0, 2 * math.pi),  # Random direction in radians
            color=color
        ))
    
    return entities
