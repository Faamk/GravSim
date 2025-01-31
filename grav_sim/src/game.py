import pygame

from grav_sim.src.config import settings
from grav_sim.src.config.settings import WindowConfig, PhysicsConfig
from grav_sim.src.core.physics.physics import PhysicsEngine
from grav_sim.src.core.physics.utils import create_default_entities
from grav_sim.src.graphics.renderer import Renderer
from grav_sim.src.input.keyboard_handler import KeyboardHandler
from grav_sim.src.input.mouse_handler import MouseHandler


class Game:
    def __init__(self):
        pygame.init()
        self.entities = create_default_entities()
        self.timescale = PhysicsConfig.DEFAULT_TIME_SCALE
        self.focused_entity = 0
        self.screen = pygame.display.set_mode((WindowConfig.WIDTH, WindowConfig.HEIGHT))
        pygame.display.set_caption("Gravity Simulator")

        self.physics = PhysicsEngine(self.entities)
        self.renderer = Renderer()
        self.mouse_handler = MouseHandler()
        self.keyboard_handler = KeyboardHandler(
            entities=self.physics.entities,
            camera=self.renderer.camera,
            time_scale=self.timescale,
        )
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            pygame.display.flip()
        pygame.quit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keyboard_handler.handle_keyboard_event(event)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                x, y = pygame.mouse.get_pos()
                button = event.button if event.type == pygame.MOUSEBUTTONDOWN else -1
                if button in (4, 5):  # Mouse wheel
                    if self.mouse_handler.creating_entity:
                        entity = self.mouse_handler.handle_click(x, y, button, self.renderer.camera)
                    else:
                        self.renderer.handle_zoom(button == 5)
                else:
                    entity = self.mouse_handler.handle_click(x, y, button, self.renderer.camera)
                    if entity:
                        self.physics.entities.append(entity)
            elif event.type == pygame.MOUSEMOTION and self.mouse_handler.mouse_held:
                x, y = pygame.mouse.get_pos()
                self.mouse_handler.handle_click(x, y, 0, self.renderer.camera)

    def update(self):
        self.physics.update(self.keyboard_handler.current_time_scale)

    def render(self):
        self.screen.fill((255, 255, 255))
        self.renderer.draw(self.screen, self.physics.entities,
                           self.mouse_handler.creating_entity,
                           self.keyboard_handler.current_time_scale)