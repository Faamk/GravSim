import math
from typing import List, Tuple, Union
from pygame.math import Vector2
from pygame import Rect
from grav_sim.src.config.settings import PhysicsConfig, BoardConfig
from grav_sim.src.core.entity.entity import Entity
from multiprocessing import Pool, cpu_count


class QuadTreeNode:
    def __init__(self, boundary: Rect, capacity: int = 100, entities: List[Entity] = None):
        self.area_rect = boundary
        self.capacity = capacity
        self.entities = [] if entities is None else entities
        self.divided = False
        self.northwest = self.northeast = self.southwest = self.southeast = None
        self.center_of_mass = Vector2(0, 0)
        self.total_mass = 0

    def subdivide(self):
        x, y, width, height = self.area_rect
        half_w, half_h = width / 2, height / 2

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
        return (self.northwest.insert(entity) or
                self.northeast.insert(entity) or
                self.southwest.insert(entity) or
                self.southeast.insert(entity))

    def insert(self, entity: Entity) -> bool:
        if not self.area_rect.colliderect(entity.realRect):
            return False

        if len(self.entities) < self.capacity and not self.divided:
            self.entities.append(entity)
            self._update_mass_center(entity)
            return True

        if not self.divided:
            self.subdivide()

        return any(child.insert(entity) for child in [self.northwest, self.northeast, self.southwest, self.southeast])

    def _update_mass_center(self, entity: Entity):
        self.center_of_mass = (self.center_of_mass * self.total_mass + entity.position * entity.mass) / (
                self.total_mass + entity.mass)
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
        self.entities = {entity.name: entity for entity in entities}  # Convert list to dictionary
        self.quad_tree = None
        self.pool = Pool(processes=cpu_count())

    @staticmethod
    def _calculate_gravitational_force(G: float, entity: Entity, attractor: Union[Entity, QuadTreeNode]) -> Vector2:
        attractor_pos = attractor.position if isinstance(attractor, Entity) else attractor.center_of_mass
        attractor_mass = attractor.mass if isinstance(attractor, Entity) else attractor.total_mass

        direction = attractor_pos - entity.position
        distance = direction.length()

        if distance <= 0:
            return Vector2(0, 0)

        force = G * entity.mass * attractor_mass / (distance * distance)
        gravity_dir = direction.normalize()
        return gravity_dir * (force / entity.mass)

    @staticmethod
    def _calculate_gravity_vector(entity: Entity, quad_tree: QuadTreeNode, time_scale: float,
                                  G: float, theta: float = 0.5) -> Vector2:
        def apply_force(node: QuadTreeNode) -> Vector2:

            direction = node.center_of_mass - entity.position
            distance = direction.length()
            if PhysicsEngine._is_empty_node(node) or distance == 0:
                return PhysicsEngine.NO_FORCE_VECTOR

            if PhysicsEngine._should_apply_direct_force(node, entity, distance, theta):
                return PhysicsEngine._calculate_gravitational_force(G, entity, node)

            if node.divided:
                return sum(
                    (apply_force(child) for child in [node.northwest, node.northeast, node.southwest, node.southeast]),
                    PhysicsEngine.NO_FORCE_VECTOR)

            return sum((PhysicsEngine._calculate_gravitational_force(G, entity, other)
                        for other in node.entities if other is not entity),
                       PhysicsEngine.NO_FORCE_VECTOR)

        return apply_force(quad_tree)

    @staticmethod
    def _is_empty_node(node: QuadTreeNode) -> bool:
        return not node or node.total_mass == 0

    @staticmethod
    def _should_apply_direct_force(node: QuadTreeNode, entity: Entity, distance: float, theta: float) -> bool:
        is_single_entity = len(node.entities) == 1
        is_self = is_single_entity and node.entities[0] is entity
        is_far_enough = node.area_rect.width / distance < theta

        return not is_self and (is_single_entity or is_far_enough)

    @staticmethod
    def _process_entity(args: Tuple[Entity, QuadTreeNode, float]) -> Entity:
        entity, quad_tree, time_scale = args

        velocity = entity.get_velocity_vector()
        gravity = PhysicsEngine._calculate_gravity_vector(
            entity=entity,
            quad_tree=quad_tree,
            time_scale=time_scale,
            G=PhysicsConfig.GRAVITY_CONSTANT * time_scale
        )

        # Update velocity and direction
        new_velocity = velocity + gravity
        entity.velocity = new_velocity.length()
        entity.direction = math.atan2(new_velocity.y, new_velocity.x)

        # Calculate new position
        movement = Vector2(
            math.cos(entity.direction) * entity.velocity * time_scale,
            math.sin(entity.direction) * entity.velocity * time_scale
        )
        new_x = entity.position.x + movement.x
        new_y = entity.position.y + movement.y

        entity.move(new_x, new_y)
        return entity

    def update(self, time_scale: float) -> None:
        self.quad_tree = QuadTreeNode(Rect(0, 0, BoardConfig.WIDTH, BoardConfig.HEIGHT))
        for entity in self.entities.values():
            self.quad_tree.insert(entity)

        update_args = [(entity, self.quad_tree, time_scale) for entity in self.entities.values()]
        updated_entities = self.pool.map(self._process_entity, update_args)

        # Update entities dictionary with new versions
        self.entities = {entity.name: entity for entity in updated_entities}

        for entity in list(self.entities.values()):
            colliding = self.quad_tree.query_range(entity.realRect)
            for other in colliding:
                if other.name != entity.name and other.name in self.entities and entity.mass > other.mass:
                    entity.consume(other)
                    del self.entities[other.name]


    def __del__(self):
        self.pool.close()
        self.pool.join()
