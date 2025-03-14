import math
from typing import Optional
from pygame.math import Vector2

from grav_sim.src.config.settings import EntityConfig
from grav_sim.src.core.entity.entity import Entity
from grav_sim.src.graphics.camera import Camera


class MouseHandler:
    def __init__(self):
        self.mouse_held = False
        self.mass = EntityConfig.DEFAULT_MASS
        self.start_pos = None
        self.creating_entity = None

    def handle_click(self, mouse_x: int, mouse_y: int, button: int, camera: Camera) -> Optional[Entity]:
        screen_pos = Vector2(mouse_x, mouse_y)
        world_pos = camera.screen_to_world_pos(screen_pos)

        if button == 1:  # Left click
            self.mouse_held = True
            self.start_pos = world_pos
            self.creating_entity = Entity(
                position=world_pos,
                density=EntityConfig.DEFAULT_DENSITY,
                mass=self.mass,
                velocity=0,
                direction=0,
                color=(0, 0, 255),
                draw_velocity=True
            )
        elif button == 0 and self.mouse_held:  # Mouse motion while held
            if self.creating_entity:
                # Update velocity and direction based on drag
                diff = world_pos - self.start_pos
                self.creating_entity.velocity = diff.length() * EntityConfig.VELOCITY_MULTIPLIER
                self.creating_entity.direction = math.atan2(diff.y, diff.x)
        elif button == -1 and self.mouse_held:  # Mouse release
            self.mouse_held = False
            result = self.creating_entity
            self.creating_entity = None
            self.start_pos = None
            return result

        return None
