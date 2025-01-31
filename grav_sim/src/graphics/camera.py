from pygame.math import Vector2
from grav_sim.src.config.settings import WindowConfig, BoardConfig


class Camera:
    def __init__(self):
        self.zoom_level = 1.0
        self.min_zoom = 0.01
        self.max_zoom = 10.0

        # Calculate the visible area
        self.viewport_width = WindowConfig.WIDTH
        self.viewport_height = WindowConfig.HEIGHT

        # Initialize position at board center
        self.position = Vector2(
            BoardConfig.WIDTH / 2,
            BoardConfig.HEIGHT / 2
        )

    def focus_on(self, x: float, y: float) -> None:
        """Center the camera on specific world coordinates"""
        self.position = Vector2(x, y)

    def zoom(self, zoom_in: bool) -> None:
        if zoom_in:
            self.zoom_level = max(self.min_zoom, self.zoom_level * 0.9)
        else:
            self.zoom_level = min(self.max_zoom, self.zoom_level * 1.1)

    def world_to_screen_pos(self, world_pos: Vector2) -> Vector2:
        """Convert world coordinates to screen coordinates"""
        # Calculate position relative to the camera's focus point
        relative_to_center = world_pos - self.position

        # Scale by zoom and center in viewport
        # Use round() to prevent subpixel jitter at high zoom levels
        screen_pos = Vector2(
            round((relative_to_center.x * self.zoom_level) + (self.viewport_width / 2)),
            round((relative_to_center.y * self.zoom_level) + (self.viewport_height / 2))
        )
        return screen_pos

    def screen_to_world_pos(self, screen_pos: Vector2) -> Vector2:
        """Convert screen coordinates to world coordinates"""
        # Calculate position relative to viewport center
        relative_to_center = Vector2(
            screen_pos.x - (self.viewport_width / 2),
            screen_pos.y - (self.viewport_height / 2)
        )

        # Scale by inverse zoom and add board center
        world_pos = Vector2(
            (relative_to_center.x / self.zoom_level) + self.position.x,
            (relative_to_center.y / self.zoom_level) + self.position.y
        )
        return world_pos

    def get_visible_area(self) -> tuple[Vector2, Vector2]:
        """Return the visible area in world coordinates (top_left, bottom_right)"""
        top_left = self.screen_to_world_pos(Vector2(0, 0))
        bottom_right = self.screen_to_world_pos(Vector2(self.viewport_width, self.viewport_height))
        return top_left, bottom_right