import pygame
from pygame.math import Vector2
from grav_sim.src.config.settings import WindowConfig, BoardConfig
from grav_sim.src.core.entity.entity import Entity


class Camera:
    def __init__(self, entity_to_track):
        self.zoom_level = 1.0
        self.min_zoom = 0.01
        self.max_zoom = 10.0

        self.viewport = pygame.Rect(0, 0, WindowConfig.WIDTH, WindowConfig.HEIGHT)
        self.entity_to_track: Entity = entity_to_track

        self.position = Vector2(BoardConfig.WIDTH / 2, BoardConfig.HEIGHT / 2)

    def focus_on(self, x: float, y: float, alpha=0.1) -> None:
        target_pos = Vector2(x, y)
        self.position = self.position.lerp(target_pos, alpha)

    def zoom(self, zoom_in: bool) -> None:
        factor = 0.9 if zoom_in else 1.1
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level * factor))

    def world_to_screen_pos(self, world_pos: Vector2) -> Vector2:
        relative_to_center = world_pos - self.position
        screen_pos = (relative_to_center.elementwise() * self.zoom_level) + Vector2(self.viewport.width / 2,
                                                                                    self.viewport.height / 2)
        return screen_pos

    def screen_to_world_pos(self, screen_pos: Vector2) -> Vector2:
        relative_to_center = screen_pos - Vector2(self.viewport.width / 2, self.viewport.height / 2)
        world_pos = (relative_to_center / self.zoom_level) + self.position
        return world_pos

    def get_visible_area(self) -> tuple[Vector2, Vector2]:
        top_left = self.screen_to_world_pos(Vector2(0, 0))
        bottom_right = self.screen_to_world_pos(Vector2(self.viewport.width, self.viewport.height))
        return top_left, bottom_right

    def update(self):
        if self.entity_to_track:
            self.focus_on(self.entity_to_track.position.x, self.entity_to_track.position.y, alpha=0.2)
