from abc import ABC

__all__ = ["MapError", "MapTooFewPointsError", "MapDimensionTooSmallError",
           "MapPointError", "MapPointUnspawnableError", "SpawnPointOutOfMapError", "UnknownResourceTypeError",
           "NoPlayerSpawnPointError"]


class MapError(ABC, Exception):
    pass


class MapPointError(MapError, ABC):
    pass


class MapTooFewPointsError(MapError):
    def __init__(self, expected: int, actual: int):
        super().__init__(f"{actual} / {expected}")


class MapDimensionTooSmallError(MapError):
    pass


class MapPointUnspawnableError(MapPointError):
    pass


class SpawnPointOutOfMapError(MapPointError):
    pass


class UnknownResourceTypeError(MapPointError):
    pass


class NoPlayerSpawnPointError(MapPointError):
    pass
