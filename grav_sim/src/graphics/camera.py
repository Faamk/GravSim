import pygame
from pygame import Rect
from pygame.math import Vector2
from grav_sim.src.config.settings import BoardConfig
from grav_sim.src.core.entity.entity import Entity


from grav_sim.src.config.settings import CameraConfig, WindowConfig

class Camera:
    def __init__(self, entity_to_track):
        self.zoom_level = CameraConfig.STARTING_ZOOM_LEVEL

        self.viewport = pygame.Rect(CameraConfig.STARTING_X, CameraConfig.STARTING_Y, WindowConfig.WIDTH, WindowConfig.HEIGHT)
        self.entity_to_track: Entity = entity_to_track

        self.position = Vector2(BoardConfig.WIDTH / 2, BoardConfig.HEIGHT / 2)

    def focus_on(self, x: float, y: float) -> None:
        self.position.x = x
        self.position.y = y

    def zoom(self, zoom_in: bool) -> None:
        factor = CameraConfig.ZOOM_IN_FACTOR if zoom_in else CameraConfig.ZOOM_OUT_FACTOR
        self.zoom_level = max(CameraConfig.MIN_ZOOM, min(CameraConfig.MAX_ZOOM, self.zoom_level * factor))

    def world_to_screen_pos(self, world_pos: Vector2) -> Vector2:
        relative_to_center = world_pos - self.position
        screen_pos = (relative_to_center.elementwise() * self.zoom_level) + Vector2(self.viewport.width / 2,
                                                                                    self.viewport.height / 2)
        return screen_pos

    def screen_to_world_pos(self, screen_pos: Vector2) -> Vector2:
        relative_to_center = screen_pos - Vector2(self.viewport.width / 2, self.viewport.height / 2)
        world_pos = (relative_to_center / self.zoom_level) + self.position
        return world_pos

    def get_visible_area(self) -> Rect:
        top_left = self.screen_to_world_pos(Vector2(self.viewport.topleft))
        return Rect(top_left.x, top_left.y, self.viewport.width / self.zoom_level,
                    self.viewport.height / self.zoom_level)

    def update(self, entities) -> None:
        if self.entity_to_track:
            self.entity_to_track = entities[self.entity_to_track.name]
            self.focus_on(self.entity_to_track.position.x, self.entity_to_track.position.y)


