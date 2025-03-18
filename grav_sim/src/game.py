import pygame

from grav_sim.src.config.settings import WindowConfig, PhysicsConfig
from grav_sim.src.core.physics.physics import PhysicsEngine
from grav_sim.src.core.physics.utils import create_random_entities, create_default_entities
from grav_sim.src.graphics.camera import Camera
from grav_sim.src.graphics.renderer import Renderer
from grav_sim.src.input.keyboard_handler import KeyboardHandler
from grav_sim.src.input.mouse_handler import MouseHandler
import pygame_menu

from grav_sim.src.menu.option_menu import OptionsMenu, Scenario


class Game:
    def __init__(self):
        pygame.init()
        self.entities = create_default_entities()
        self.timescale = PhysicsConfig.DEFAULT_TIME_SCALE
        self.screen = pygame.display.set_mode((WindowConfig.WIDTH, WindowConfig.HEIGHT))
        pygame.display.set_caption("Gravity Simulator")

        self.physics = PhysicsEngine(self.entities)
        self.camera = Camera(entity_to_track=None)
        self.renderer = Renderer(camera=self.camera)
        self.mouse_handler = MouseHandler()
        self.keyboard_handler = KeyboardHandler(
            entities=self.physics.entities,
            camera=self.renderer.camera,
            time_scale=self.timescale,
        )
        self.running = False
        self.menu = OptionsMenu(self.set_scenario, self.start_game)


    def set_scenario(self, value, scenario):
        self.physics = PhysicsEngine(Scenario[scenario].value)


    def start_game(self):
        self.menu.disable()  # Disable the menu
        self.main_loop()  # Start the main game loop

    def menu_loop(self):
        self.menu.mainloop(self.screen)
        self.main_loop()

    def main_loop(self):
        self.running = True
        while self.running:
            frame_start = pygame.time.get_ticks()

            input_start = pygame.time.get_ticks()
            self.handle_input()
            input_time = pygame.time.get_ticks() - input_start

            update_start = pygame.time.get_ticks()
            self.update()
            update_time = pygame.time.get_ticks() - update_start

            render_start = pygame.time.get_ticks()
            self.render()
            pygame.display.flip()
            render_time = pygame.time.get_ticks() - render_start

            total_frame_time = pygame.time.get_ticks() - frame_start

            print(f"Frame timing (ms): Input: {input_time}, Update: {update_time}, Render: {render_time}, Total: {total_frame_time}")


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
                        entity.draw_velocity = False
                        self.physics.entities[entity.name] = entity
            elif event.type == pygame.MOUSEMOTION and self.mouse_handler.mouse_held:
                x, y = pygame.mouse.get_pos()
                self.mouse_handler.handle_click(x, y, 0, self.renderer.camera)

    def update(self):
        self.physics.update(self.keyboard_handler.time_scale)
        self.camera.update(self.physics.entities)

    def render(self):
        self.renderer.draw(self.screen, list(self.physics.entities.values()), self.mouse_handler.creating_entity,
                           self.keyboard_handler.time_scale)
