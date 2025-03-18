import pygame

from ..core.entity.entity import Entity
from ..graphics.camera import Camera


class KeyboardHandler:
    def __init__(self, entities: list[Entity], camera: Camera, time_scale: float) -> None:
        self.time_scale: float = time_scale
        self.entities: list[Entity] = entities
        self.camera: Camera = camera

    def handle_keyboard_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._process_key(event.key)

    def _process_key(self, key: int) -> None:
        actions = {
            pygame.K_PERIOD: self._increase_time_scale,
            pygame.K_COMMA: self._decrease_time_scale,
            pygame.K_SPACE: self._pause_game,
        }

        if key in actions:
            actions[key]()
        elif pygame.K_1 <= key <= pygame.K_9:
            self._track_entity(key)

    def _increase_time_scale(self) -> None:
        self.time_scale = min(self.time_scale * 2, 1000.0)

    def _decrease_time_scale(self) -> None:
        self.time_scale = max(self.time_scale / 2, 0.25)

    def _pause_game(self) -> None:
        self.time_scale = 0.0

    def _track_entity(self, key: int) -> None:
        entity_keys = list(self.entities.keys())
        index = key - pygame.K_1
        if 0 <= index < len(entity_keys):
            entity_key = entity_keys[index]
            self.camera.entity_to_track = self.entities[entity_key]
