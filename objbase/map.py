from dataclasses import dataclass
from typing import List, Dict

from models import Model, ModelDefaultValueExt
from models.field import IntegerField, MultiDimensionalArrayField, FlagField, ModelField, ArrayField, DictionaryField
from rxtoolbox.flags import FlagCodeEnum
from objbase import BattleObject
from exception import (
    MapTooFewPointsError, MapDimensionTooSmallError,
    MapPointUnspawnableError, SpawnPointOutOfMapError, NoPlayerSpawnPointError, UnknownResourceTypeError
)

__all__ = ["MapPointStatus", "MapPointResource", "MapPointModel", "MapCoordinateModel", "MapModel", "MapTemplate"]


# region Enums / Flags

class MapPointStatus(FlagCodeEnum):
    """
    Type of the map point.

    ``UNAVAILABLE`` - The map point is unavailable for the map.
    ``EMPTY`` - The map point is empty.
    ``PLAYER`` - A player is on the map point.
    ``CHEST`` - A chest is on the map point.
    ``MONSTER`` - A monster is on the map point.
    ``FIELD_BOSS`` - A field boss is on the map point.
    """

    @classmethod
    def default(cls):
        return MapPointStatus.UNAVAILABLE

    UNAVAILABLE = 0
    EMPTY = 1
    PLAYER = 2
    CHEST = 3
    MONSTER = 4
    FIELD_BOSS = 5

    @property
    def is_map_point(self):
        return self.code > 0


class MapPointResource(FlagCodeEnum):
    """
    Deployable resource type of the map point.

    ``CHEST`` - Chest could be spawned on the map point.
    ``MONSTER`` - Monster could be spawned on the map point.
    ``FIELD_BOSS`` - Field boss could be spawned on the map point.
    """
    CHEST = 3
    MONSTER = 4
    FIELD_BOSS = 5


# endregion


# region Special model field

class MapPointStatusField(FlagField):
    FLAG_TYPE = MapPointStatus


class BattleObjectField(ModelField):
    def __init__(self, key, **kwargs):
        super().__init__(key, BattleObject, **kwargs)

    @property
    def expected_types(self):
        return super().expected_types + tuple(BattleObject.__subclasses__())


# endregion


# region Models

class MapCoordinateModel(Model):
    """
    Map point coordinate to be stored in the database under ``MapPointModel.Coord``.
    """
    WITH_OID = False

    X = IntegerField("x", default=ModelDefaultValueExt.Required)
    Y = IntegerField("y", default=ModelDefaultValueExt.Required)


class MapPointModel(Model):
    """
    Map point to be stored in the database under ``MapModel.PointStatus``.
    """
    WITH_OID = False

    PointStatus = MapPointStatusField("s", default=ModelDefaultValueExt.Required)
    Obj = BattleObjectField("obj", default=None)
    Coord = ModelField("c", MapCoordinateModel, default=ModelDefaultValueExt.Required)
    Resource = ArrayField("res", MapPointResource)


class MapModel(Model):
    Width = IntegerField("w", positive_only=True, default=ModelDefaultValueExt.Required)
    Height = IntegerField("h", positive_only=True, default=ModelDefaultValueExt.Required)
    PointStatus = MultiDimensionalArrayField("pt", 2, MapPointModel, default=ModelDefaultValueExt.Required)
    ResourcePoints = DictionaryField("res", default=ModelDefaultValueExt.Required)


# endregion


@dataclass
class MapTemplate:
    """
    Map template.

    This could be converted to :class:`MapModel` and
    store to the database (initialize a game) by calling `to_model()`.
    """
    MIN_WIDTH = 9
    MIN_HEIGHT = 9
    MIN_AVAILABLE_NODES = 81

    width: int
    height: int
    points: List[List[MapPointStatus]]
    resources: Dict[MapPointResource, List[MapCoordinateModel]]

    def __post_init__(self):
        if self.width < MapTemplate.MIN_WIDTH or self.height < MapTemplate.MIN_HEIGHT:
            raise MapDimensionTooSmallError()

        available_nodes = sum(sum(1 if p.is_map_point else 0 for p in row) for row in self.points)
        if available_nodes < MapTemplate.MIN_AVAILABLE_NODES:
            raise MapTooFewPointsError(MapTemplate.MIN_AVAILABLE_NODES, available_nodes)

        if not any(any(p == MapPointStatus.PLAYER for p in row) for row in self.points):
            raise NoPlayerSpawnPointError()

        # Check resource points
        for coords in self.resources.values():
            for coord in coords:
                x = coord.x
                y = coord.y

                # Check out of map
                if x >= self.width or y >= self.height:
                    raise SpawnPointOutOfMapError()

                if not self.points[x][y].is_map_point:
                    raise MapPointUnspawnableError()

    def tighten(self):
        pass  # TODO TEST

    def respawn(self):
        pass  # TODO TEST

    def to_model(self) -> MapModel:
        return MapModel(Width=self.width, Height=self.height, PointStatus=self.points, ResourcePoints=self.resources)

    @staticmethod
    def load_from_file(path: str) -> 'MapTemplate':
        """
        Load the template from a map file.

        This parsing method checks logic error, but not the format error.

        .. seealso::
            See `res/map/spec.md` for the specification of the map file.

        :param path: path of the file
        :return: a parsed `MapTemplate`
        """
        with open(path) as f:
            lines = f.read().split("\n")

        # Parse dimension
        width, height = [int(n) for n in lines.pop(0).split(" ", 2)]

        # Parse initial map points
        points: List[List[MapPointStatus]] = [[] for _ in range(width)]
        for y in range(height):
            for x, elem in zip(range(width), lines.pop(0)):
                points[x].append(MapPointStatus.cast(elem))

        # parse resource spawning location
        res_dict: Dict[MapPointResource, List[MapCoordinateModel]] = {}
        for line in lines:
            type_int, *coords = line.split(" ")

            try:
                res_type = MapPointResource.cast(type_int)
            except ValueError:
                raise UnknownResourceTypeError()

            coords = [coord.split(",", 2) for coord in coords]
            res_dict[res_type] = [MapCoordinateModel(X=int(x), Y=int(y)) for x, y in coords]

        return MapTemplate(width, height, points, res_dict)
