class WindowConfig:
    WIDTH = 1000
    HEIGHT = 1000

class CameraConfig:
    MIN_ZOOM = 0.01
    MAX_ZOOM = 10.0
    STARTING_ZOOM_LEVEL = 1
    STARTING_X = 0
    STARTING_Y = 0
    ZOOM_IN_FACTOR = 0.9
    ZOOM_OUT_FACTOR = 1.1


class BoardConfig:
    WIDTH = 10000
    HEIGHT = 10000


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
