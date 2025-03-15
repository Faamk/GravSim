class WindowConfig:
    WIDTH = 1000
    HEIGHT = 1000

class CameraConfig:
    MIN_ZOOM = 0.005
    MAX_ZOOM = 100.0
    STARTING_ZOOM_LEVEL = 0.01
    STARTING_X = 0
    STARTING_Y = 0
    ZOOM_IN_FACTOR = 0.9
    ZOOM_OUT_FACTOR = 1.1

class RendererConfig:
    VELOCITY_SCALE = 100
    BASE_ARROW_LENGTH = 20


class BoardConfig:
    WIDTH = 100000
    HEIGHT = 100000


class PhysicsConfig:
    GRAVITY_CONSTANT = 0.1
    DEFAULT_TIME_SCALE = 1.0
    MAX_TIME_SCALE = 10.0
    MIN_TIME_SCALE = 0.1


class EntityConfig:
    DEFAULT_COLOR = (255, 0, 0)
    DEFAULT_MASS = 10.0
    DEFAULT_DENSITY = 0.1
    VELOCITY_MULTIPLIER = 0.01
