import pygame
from typing import List, Optional
import math
from pygame.math import Vector2

from grav_sim.src.config.settings import WindowConfig, RendererConfig
from grav_sim.src.core.entity.entity import Entity


class Renderer:
    def __init__(self, camera):
        self.font = pygame.font.Font(None, 24)
        self.camera = camera
        self.overlay_surface = pygame.Surface((200, WindowConfig.HEIGHT), pygame.SRCALPHA)
        self.text_cache = {}

    def draw(self, canvas: pygame.Surface, entities: List[Entity], creating_entity: Optional[Entity], time_scale: float) -> None:
        canvas.fill((0, 0, 0))

        all_entities = entities + ([creating_entity] if creating_entity else [])
        self._draw_entities(canvas, all_entities)
        self._draw_velocity_arrows(canvas, all_entities)
        self._draw_overlay(canvas, entities, creating_entity, time_scale)

    def _draw_entities(self, canvas: pygame.Surface, entities: List[Entity]) -> None:
        for entity in entities:
            if not entity.realRect.colliderect(self.camera.get_visible_area()):
                continue

            world_diameter = entity.radius * 2
            screen_diameter = max(1, round(world_diameter * self.camera.zoom_level))
            screen_pos = self.camera.world_to_screen_pos(entity.position)

            if screen_diameter == 1:
                canvas.set_at((round(screen_pos.x), round(screen_pos.y)), entity.color)
            else:
                pygame.draw.circle(
                    canvas,
                    entity.color,
                    (round(screen_pos.x), round(screen_pos.y)),
                    round(screen_diameter / 2)
                )

    def _draw_velocity_arrows(self, canvas: pygame.Surface, entities: List[Entity]) -> None:
        for entity in entities:
            if entity.velocity > 0 and entity.draw_velocity:
                screen_pos = self.camera.world_to_screen_pos(entity.position)
                arrow_length = (RendererConfig.BASE_ARROW_LENGTH +
                              (entity.velocity * RendererConfig.VELOCITY_SCALE)) * self.camera.zoom_level

                end_point = Vector2(
                    screen_pos.x + math.cos(entity.direction) * arrow_length,
                    screen_pos.y + math.sin(entity.direction) * arrow_length
                )

                # Draw arrow line
                pygame.draw.line(canvas, (0, 255, 0), screen_pos, end_point, 2)

                # Draw arrow head as triangle
                head_length = 10
                head_angle = math.pi / 6

                points = [
                    end_point,
                    Vector2(
                        end_point.x - head_length * math.cos(entity.direction + head_angle),
                        end_point.y - head_length * math.sin(entity.direction + head_angle)
                    ),
                    Vector2(
                        end_point.x - head_length * math.cos(entity.direction - head_angle),
                        end_point.y - head_length * math.sin(entity.direction - head_angle)
                    )
                ]

                pygame.draw.polygon(canvas, (0, 255, 0), points)

    def _draw_overlay(self, canvas: pygame.Surface, entities: List[Entity],
                     creating_entity: Optional[Entity], time_scale: float) -> None:
        self.overlay_surface.fill((0, 0, 0, 0))

        # Draw time scale and zoom
        time_text = self._get_cached_text(f"Time Scale: {time_scale:.2f}x")
        zoom_text = self._get_cached_text(f"Zoom: {self.camera.zoom_level:.3f}x")
        canvas.blit(time_text, (WindowConfig.WIDTH - 150, 10))
        canvas.blit(zoom_text, (10, 10))

        # Draw entity stats
        y_offset = 50
        line_height = 20
        #for entity in entities:
          #  self._draw_entity_stats(self.overlay_surface, entity, y_offset, line_height)
         #   y_offset += line_height * 2 + 5

        if creating_entity:
            self._draw_entity_stats(self.overlay_surface, creating_entity, y_offset, line_height)

        canvas.blit(self.overlay_surface, (0, 0))

    def handle_zoom(self, zoom_in: bool) -> None:
        self.camera.zoom(zoom_in)
        self.text_cache.clear()

    def _draw_entity_stats(self, surface: pygame.Surface, entity: Entity,
                          y_offset: int, line_height: int) -> None:
        pygame.draw.rect(surface, entity.color, (10, y_offset, 200, line_height * 2))
        mass_text = self._get_cached_text(f"Mass: {entity.mass:.1f}")
        vel_text = self._get_cached_text(f"Velocity: {entity.velocity:.1f}")
        surface.blit(mass_text, (15, y_offset))
        surface.blit(vel_text, (15, y_offset + line_height))

    def _get_cached_text(self, text: str) -> pygame.Surface:
        if text not in self.text_cache:
            self.text_cache[text] = self.font.render(text, True, (255, 255, 255))
        return self.text_cache[text]
