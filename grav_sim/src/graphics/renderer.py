import pygame
from typing import List, Optional
import math
from pygame.math import Vector2

from grav_sim.src.config.settings import WindowConfig
from grav_sim.src.core.entity.entity import Entity
from grav_sim.src.graphics.camera import Camera


class Renderer:
    def __init__(self, camera):
        self.font = pygame.font.Font(None, 24)
        self.BASE_ARROW_LENGTH = 20
        self.VELOCITY_SCALE = 100
        self.camera = camera

        # Create layers for different rendering purposes
        self.entity_group = pygame.sprite.Group()
        self.overlay_surface = pygame.Surface((200, WindowConfig.HEIGHT), pygame.SRCALPHA)

        # Cache for surfaces
        self.text_cache = {}

    def draw(self, canvas: pygame.Surface, entities: List[Entity],
             creating_entity: Optional[Entity], time_scale: float) -> None:
        # Clear canvas
        canvas.fill((255, 255, 255))

        # Update and draw all entities
        all_entities = entities + ([creating_entity] if creating_entity else [])
        self._update_entities(all_entities)

        # Draw entities
        self.entity_group.draw(canvas)

        # Draw velocity arrows
        self._draw_velocity_arrows(canvas, all_entities)

        # Draw overlay
        self._draw_overlay(canvas, entities, creating_entity, time_scale)

    def _update_entities(self, entities: List[Entity]) -> None:
        self.entity_group.empty()

        for entity in entities:
            # Calculate render size based on world radius and zoom
            world_diameter = entity.radius * 2
            screen_diameter = max(1, round(world_diameter * self.camera.zoom_level))

            # Create visual surface
            surface = pygame.Surface((screen_diameter, screen_diameter), pygame.SRCALPHA)
            pygame.draw.circle(surface, entity.color,
                             (screen_diameter // 2, screen_diameter // 2),
                             screen_diameter // 2)
            entity.image = surface

            # Update sprite rect for rendering only
            screen_pos = self.camera.world_to_screen_pos(entity.position)
            entity.rect = pygame.Rect(
                round(screen_pos.x - (screen_diameter // 2)),
                round(screen_pos.y - (screen_diameter // 2)),
                screen_diameter,
                screen_diameter
            )

            self.entity_group.add(entity)

    def _draw_velocity_arrows(self, canvas: pygame.Surface, entities: List[Entity]) -> None:
        for entity in entities:
            if entity.velocity > 0:
                screen_pos = self.camera.world_to_screen_pos(entity.position)
                arrow_length = (self.BASE_ARROW_LENGTH +
                                (entity.velocity * self.VELOCITY_SCALE)) * self.camera.zoom_level
                end_point = Vector2(
                    screen_pos.x + math.cos(entity.direction) * arrow_length,
                    screen_pos.y + math.sin(entity.direction) * arrow_length
                )
                pygame.draw.line(canvas, (0, 255, 0), screen_pos, end_point, 2)
                self._draw_arrow_head(canvas, end_point, entity.direction, (0, 255, 0))

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
