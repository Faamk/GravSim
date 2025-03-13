from pygame.math import Vector2
import pygame
from grav_sim.src.config.settings import WindowConfig, BoardConfig


class Camera:
    def __init__(self):
        self.zoom_level = 1.0
        self.min_zoom = 0.01
        self.max_zoom = 10.0

        # Create a viewport rect for the visible area
        self.viewport = pygame.Rect(0, 0,
                                    int(WindowConfig.WIDTH / self.zoom_level),
                                    int(WindowConfig.HEIGHT / self.zoom_level)
                                    )

        # Initialize position at board center
        self.viewport.center = (BoardConfig.WIDTH // 2, BoardConfig.HEIGHT // 2)

    def focus_on(self, x: float, y: float) -> None:
        """Center the camera on specific world coordinates"""
        self.viewport.center = (int(x), int(y))

    def zoom(self, zoom_in: bool) -> None:
        old_zoom = self.zoom_level
        if zoom_in:
            self.zoom_level = min(self.max_zoom, self.zoom_level * 1.1)
        else:
            self.zoom_level = max(self.min_zoom, self.zoom_level * 0.9)

        # Adjust viewport size based on new zoom level
        center = self.viewport.center
        self.viewport.width = int(WindowConfig.WIDTH / self.zoom_level)
        self.viewport.height = int(WindowConfig.HEIGHT / self.zoom_level)
        self.viewport.center = center

    def apply_to_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply camera transform to a surface and return the visible portion"""
        try:
            # Get the portion of the surface visible in our viewport
            subsurface = surface.subsurface(self.viewport)

            # Scale it to match our zoom level
            scaled_size = (WindowConfig.WIDTH, WindowConfig.HEIGHT)
            return pygame.transform.scale(subsurface, scaled_size)
        except ValueError:
            # If subsurface fails, return a blank surface
            return pygame.Surface((WindowConfig.WIDTH, WindowConfig.HEIGHT))

    def world_to_screen_pos(self, world_pos: Vector2) -> Vector2:
        """Convert world coordinates to screen coordinates"""
        # Convert from world space to viewport space
        viewport_x = (world_pos.x - self.viewport.left)
        viewport_y = (world_pos.y - self.viewport.top)

        # Scale to screen space
        screen_x = viewport_x * (WindowConfig.WIDTH / self.viewport.width)
        screen_y = viewport_y * (WindowConfig.HEIGHT / self.viewport.height)

        return Vector2(screen_x, screen_y)

    def screen_to_world_pos(self, screen_pos: Vector2) -> Vector2:
        """Convert screen coordinates to world coordinates"""
        # Scale from screen space to viewport space
        viewport_x = screen_pos.x * (self.viewport.width / WindowConfig.WIDTH)
        viewport_y = screen_pos.y * (self.viewport.height / WindowConfig.HEIGHT)

        # Convert to world space
        world_x = viewport_x + self.viewport.left
        world_y = viewport_y + self.viewport.top

        return Vector2(world_x, world_y)

    def get_visible_area(self) -> tuple[Vector2, Vector2]:
        """Return the visible area in world coordinates (top_left, bottom_right)"""
        return (
            Vector2(self.viewport.topleft),
            Vector2(self.viewport.bottomright)
        )