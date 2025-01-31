from typing import Optional

import pygame

from ..core.entity.entity import Entity
from ..graphics.camera import Camera


class KeyboardHandler:
    def __init__(self, entities: list[Entity], camera: Camera, time_scale: float):
        self.time_scale = time_scale
        self.focused_entity: Optional[Entity] = None
        self.entities = entities
        self.camera = camera

    def handle_keyboard_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard events and update game state accordingly"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)

    def _handle_keydown(self, key: int) -> None:
        """Handle key press events"""
        if key == pygame.K_PERIOD:
            self.time_scale = self._adjust_time_scale(increase=True)
        elif key == pygame.K_COMMA:
            self.time_scale = self._adjust_time_scale(increase=False)
        elif key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        # Handle number keys 1-9
        elif pygame.K_1 <= key <= pygame.K_9:
            index = key - pygame.K_1  # Convert key to 0-based index
            if index < len(self.entities):
                entity = self.entities[index]
                self.camera.focus_on(entity.position.x, entity.position.y)
                self.focused_entity = entity

    def _adjust_time_scale(self, increase: bool) -> float:
        """Adjust the time scale up or down"""
        if increase:
            return self.time_scale * 2
        return self.time_scale / 2

    @property
    def current_time_scale(self) -> float:
        return self.time_scale