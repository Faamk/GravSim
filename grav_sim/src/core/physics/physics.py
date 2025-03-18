import math
from typing import List, Tuple, Union

import pygame
from pygame.math import Vector2
from pygame import Rect
from grav_sim.src.config.settings import PhysicsConfig, BoardConfig
from grav_sim.src.core.entity.entity import Entity
from multiprocessing import Pool, cpu_count

# QuadTree Node to manage space partitioning
class QuadTreeNode:
    def __init__(self, boundary: Rect, capacity: int = 50):
        self.area_rect = boundary
        self.capacity = capacity
        self.entities = []
        self.divided = False
        self.northwest = self.northeast = self.southwest = self.southeast = None
        self.center_of_mass = Vector2(0, 0)
        self.total_mass = 0

    def subdivide(self):
        x, y, w, h = self.area_rect
        half_w, half_h = w / 2, h / 2

        self.northwest, self.northeast, self.southwest, self.southeast = (
            QuadTreeNode(Rect(x, y, half_w, half_h)),
            QuadTreeNode(Rect(x + half_w, y, half_w, half_h)),
            QuadTreeNode(Rect(x, y + half_h, half_w, half_h)),
            QuadTreeNode(Rect(x + half_w, y + half_h, half_w, half_h))
        )
        self.divided = True
        for entity in self.entities:
            self._insert_to_children(entity)
        self.entities.clear()

    def _insert_to_children(self, entity: Entity) -> bool:
        return any(child.insert(entity) for child in [self.northwest, self.northeast, self.southwest, self.southeast])

    def insert(self, entity: Entity) -> bool:
        if not self.area_rect.colliderect(entity.realRect):
            return False
        if len(self.entities) < self.capacity and not self.divided:
            self.entities.append(entity)
            self._update_mass_center(entity)
            return True
        if not self.divided:
            self.subdivide()
        return self._insert_to_children(entity)

    def _update_mass_center(self, entity: Entity):
        self.center_of_mass = (self.center_of_mass * self.total_mass + entity.position * entity.mass) / (self.total_mass + entity.mass)
        self.total_mass += entity.mass

    def query_range(self, range_rect: Rect) -> List[Entity]:
        if not self.area_rect.colliderect(range_rect):
            return []
        found = [e for e in self.entities if range_rect.colliderect(e.realRect)]
        if self.divided:
            for child in [self.northwest, self.northeast, self.southwest, self.southeast]:
                found.extend(child.query_range(range_rect))
        return found

class PhysicsEngine:
    NO_FORCE_VECTOR = Vector2(0, 0)

    def __init__(self, entities: List[Entity]):
        self.entities = {entity.name: entity for entity in entities}
        self.quad_tree = None
        self.pool = Pool(processes=cpu_count())

    @staticmethod
    def _calculate_gravitational_force(G: float, entity: Entity, attractor: Union[Entity, QuadTreeNode]) -> Vector2:
        attractor_pos = attractor.position if isinstance(attractor, Entity) else attractor.center_of_mass
        attractor_mass = attractor.mass if isinstance(attractor, Entity) else attractor.total_mass
        direction = attractor_pos - entity.position
        distance = max(direction.length(), 1e-5)
        force = G * entity.mass * attractor_mass / (distance * distance)
        return direction.normalize() * (force / entity.mass)

    @staticmethod
    def _calculate_gravity_vector(entity: Entity, quad_tree: QuadTreeNode, G: float, theta: float = 0.5) -> Vector2:
        def apply_force(node: QuadTreeNode) -> Vector2:
            direction = node.center_of_mass - entity.position
            distance = max(direction.length(), 1e-5)
            if node.total_mass == 0:
                return PhysicsEngine.NO_FORCE_VECTOR
            if len(node.entities) == 1 and node.entities[0] is entity:
                return PhysicsEngine.NO_FORCE_VECTOR
            if node.area_rect.width / distance < theta or len(node.entities) == 1:
                return PhysicsEngine._calculate_gravitational_force(G, entity, node)
            if node.divided:
                return sum(
                    (apply_force(child) for child in [node.northwest, node.northeast, node.southwest, node.southeast]),
                    PhysicsEngine.NO_FORCE_VECTOR)
            return sum((PhysicsEngine._calculate_gravitational_force(G, entity, other) for other in node.entities if
                        other is not entity), PhysicsEngine.NO_FORCE_VECTOR)

        initial_velocity = entity.get_velocity_vector().length()
        gravity_vector = apply_force(quad_tree)
        new_velocity = (entity.get_velocity_vector() + gravity_vector).length()

        if new_velocity > 2 * initial_velocity:
            print(f"High velocity increase detected for {entity.name}: {initial_velocity} -> {new_velocity}")

        return gravity_vector

    @staticmethod
    def _process_entity(args: Tuple[Entity, QuadTreeNode, float]) -> Entity:
        entity, quad_tree, time_scale = args
        velocity = entity.get_velocity_vector()
        gravity = PhysicsEngine._calculate_gravity_vector(entity, quad_tree, PhysicsConfig.GRAVITY_CONSTANT * time_scale)

        new_velocity = velocity + gravity
        entity.velocity = new_velocity.length()
        entity.direction = math.atan2(new_velocity.y, new_velocity.x)
        movement = new_velocity * time_scale
        entity.move(entity.position.x + movement.x, entity.position.y + movement.y)
        return entity

    def get_colliding_pairs(self):
        colliding_pairs = set()
        for entity in self.entities.values():
            for other in self.quad_tree.query_range(entity.realRect):
                if entity.name != other.name and self._check_collision(entity, other):
                    colliding_pairs.add(frozenset([entity.name, other.name]))
        return colliding_pairs

    def _check_collision(self, entity1: Entity, entity2: Entity) -> bool:
        mask1 = pygame.mask.from_surface(entity1.collision_mask)
        mask2 = pygame.mask.from_surface(entity2.collision_mask)

        offset_x = int(entity2.position.x - entity1.position.x)
        offset_y = int(entity2.position.y - entity1.position.y)

        return mask1.overlap(mask2, (offset_x, offset_y)) is not None



    def handle_collisions(self):
        new_entities = {e.name: e for e in self.entities.values()}

        def resolve_collision(pair):
            e1, e2 = pair
            if e1 in new_entities and e2 in new_entities:
                larger, smaller = sorted([new_entities[e1], new_entities[e2]], key=lambda x: -x.mass)
                larger.consume(smaller)
                del new_entities[smaller.name]

        list(map(resolve_collision, self.get_colliding_pairs()))

        return new_entities

    def update(self, time_scale: float) -> None:
        self.quad_tree = QuadTreeNode(Rect(0, 0, BoardConfig.WIDTH, BoardConfig.HEIGHT))
        for entity in self.entities.values():
            self.quad_tree.insert(entity)

        update_args = [(entity, self.quad_tree, time_scale) for entity in self.entities.values()]
        updated_entities = self.pool.map(self._process_entity, update_args)
        self.entities = {entity.name: entity for entity in updated_entities}

        # Step 3: Handle collisions after gravitational effects
        self.entities = self.handle_collisions()

    def __del__(self):
        self.pool.close()
        self.pool.join()

