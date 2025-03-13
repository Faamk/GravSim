import pygame
from typing import List, Optional
import math
from pygame.math import Vector2

from grav_sim.src.config.settings import WindowConfig, BoardConfig
from grav_sim.src.core.entity.entity import Entity
from grav_sim.src.graphics.camera import Camera


class Renderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.BASE_ARROW_LENGTH = 20
        self.VELOCITY_SCALE = 100
        self.camera = Camera()

        # Create the world surface with BoardConfig dimensions
        self.world_surface = pygame.Surface((BoardConfig.WIDTH, BoardConfig.HEIGHT))

        # Create overlay surface for UI elements
        self.overlay_surface = pygame.Surface((200, WindowConfig.HEIGHT), pygame.SRCALPHA)

        # Cache for surfaces
        self.text_cache = {}

    def draw(self, canvas: pygame.Surface, entities: List[Entity],
             creating_entity: Optional[Entity], time_scale: float) -> None:
        # Clear world surface
        self.world_surface.fill((255, 255, 255))

        # Draw all entities to world surface
        all_entities = entities + ([creating_entity] if creating_entity else [])
        self._draw_entities(self.world_surface, all_entities)
        self._draw_velocity_arrows(self.world_surface, all_entities)

        # Apply camera transform to world surface and draw to canvas
        transformed_surface = self.camera.apply_to_surface(self.world_surface)
        canvas.blit(transformed_surface, (0, 0))

        # Draw overlay (UI elements) directly to canvas
        self._draw_overlay(canvas, entities, creating_entity, time_scale)

    def _draw_entities(self, surface: pygame.Surface, entities: List[Entity]) -> None:
        for entity in entities:
            # Convert world position to screen position
            screen_pos = self.camera.world_to_screen_pos(entity.position)

            # Scale radius based on zoom
            radius = max(1, round(entity.radius))

            pygame.draw.circle(
                surface,
                entity.color,
                (int(screen_pos.x), int(screen_pos.y)),
                radius
            )

    def _draw_velocity_arrows(self, surface: pygame.Surface, entities: List[Entity]) -> None:
        for entity in entities:
            if entity.velocity > 0:
                start_pos = entity.position
                arrow_length = self.BASE_ARROW_LENGTH + (entity.velocity * self.VELOCITY_SCALE)
                end_pos = Vector2(
                    start_pos.x + math.cos(entity.direction) * arrow_length,
                    start_pos.y + math.sin(entity.direction) * arrow_length
                )
                pygame.draw.line(surface, (0, 255, 0), start_pos, end_pos, 2)
                self._draw_arrow_head(surface, end_pos, entity.direction, (0, 255, 0))

    def _draw_overlay(self, canvas: pygame.Surface, entities: List[Entity],
                      creating_entity: Optional[Entity], time_scale: float) -> None:
        self.overlay_surface.fill((0, 0, 0, 0))

        # Draw time scale and zoom
        time_text = self._get_cached_text(f"Time Scale: {time_scale:.2f}x", (0, 0, 0))
        zoom_text = self._get_cached_text(f"Zoom: {self.camera.zoom_level:.2f}x", (0, 0, 0))
        canvas.blit(time_text, (WindowConfig.WIDTH - 150, 10))
        canvas.blit(zoom_text, (10, 10))

        # Draw entity stats
        y_offset = 50
        line_height = 20
        for entity in entities:
            self._draw_entity_stats(self.overlay_surface, entity, y_offset, line_height)
            y_offset += line_height * 2 + 5

        if creating_entity:
            self._draw_entity_stats(self.overlay_surface, creating_entity, y_offset, line_height)

        canvas.blit(self.overlay_surface, (0, 0))

    def handle_zoom(self, zoom_in: bool) -> None:
        self.camera.zoom(zoom_in)
        self.text_cache.clear()

    def _draw_arrow_head(self, surface: pygame.Surface, pos: Vector2,
                         angle: float, color: tuple) -> None:
        head_length = 10
        head_angle = math.pi / 6

        angle1 = angle + head_angle
        angle2 = angle - head_angle

        point1 = Vector2(
            pos.x - head_length * math.cos(angle1),
            pos.y - head_length * math.sin(angle1)
        )
        point2 = Vector2(
            pos.x - head_length * math.cos(angle2),
            pos.y - head_length * math.sin(angle2)
        )

        pygame.draw.polygon(surface, color, [pos, point1, point2])

    def _draw_entity_stats(self, surface: pygame.Surface, entity: Entity,
                           y_offset: int, line_height: int) -> None:
        pygame.draw.rect(surface, entity.color, (10, y_offset, 200, line_height * 2))
        mass_text = self._get_cached_text(f"Mass: {entity.mass:.1f}", (0, 0, 0))
        vel_text = self._get_cached_text(f"Velocity: {entity.velocity:.1f}", (0, 0, 0))
        surface.blit(mass_text, (15, y_offset))
        surface.blit(vel_text, (15, y_offset + line_height))

    def _get_cached_text(self, text: str, color: tuple) -> pygame.Surface:
        key = (text, color)
        if key not in self.text_cache:
            self.text_cache[key] = self.font.render(text, True, color)
        return self.text_cache[key]