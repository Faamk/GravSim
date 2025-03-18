from enum import Enum
from typing import List

import pygame_menu
from pygame_menu import Menu

from grav_sim.src.core.entity.entity import Entity
from grav_sim.src.core.physics.utils import create_default_entities, create_random_entities, \
    create_collision_test_entities


class Scenario(Enum):
    title: str
    entities: List[Entity]

    SOLAR_SYSTEM = create_default_entities()
    RANDOM_GRAVITY = create_random_entities(num_entities=1000, max_mass=1000, max_velocity=1)
    COLLISION_TEST = create_collision_test_entities()  # New Scenario for testing collision


class OptionsMenu(Menu):
    def __init__(self, set_scenario, start_game):
        super().__init__("Scenarios", 600, 400, theme=pygame_menu.themes.THEME_DARK)
        self.add.selector("Scenario: ", [(s.name, s.name) for s in Scenario],
                           onchange=set_scenario)
        self.add.button("Load", start_game)
        self.enable()