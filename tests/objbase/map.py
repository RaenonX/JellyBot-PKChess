from unittest import TestCase

from objbase import (
    MapTemplate, MapPointStatus, MapPointResource, MapCoordinateModel, MapPointModel, MapModel
)
from exception import (
    MapTooFewPointsError, MapDimensionTooSmallError,
    MapPointUnspawnableError, SpawnPointOutOfMapError, NoPlayerSpawnPointError, UnknownResourceTypeError
)

__all__ = ["TestMapTemplate"]


class TestMapTemplate(TestCase):
    def test(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(w)] for _ in range(h)], {})

    def test_insuf_width(self):
        w = MapTemplate.MIN_WIDTH - 1
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(MapDimensionTooSmallError):
            MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(w)] for _ in range(w)], {})

    def test_insuf_height(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT - 1

        with self.assertRaises(MapDimensionTooSmallError):
            MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(w)] for _ in range(h)], {})

    def test_insuf_points(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(MapTooFewPointsError):
            MapTemplate(w, h,
                        [[MapPointStatus.EMPTY for _ in range(w)] for _ in range(h - 2)]
                        + [
                            [MapPointStatus.UNAVAILABLE for _ in range(w)]
                            + [MapPointStatus.PLAYER for _ in range(w)]
                        ],
                        {})

    def test_unspawnable(self):
        w = MapTemplate.MIN_WIDTH + 1
        h = MapTemplate.MIN_HEIGHT + 1

        with self.assertRaises(MapPointUnspawnableError):
            MapTemplate(w, h,
                        [[MapPointStatus.PLAYER for _ in range(w)] for _ in range(h - 1)]
                        + [[MapPointStatus.UNAVAILABLE for _ in range(w)]],
                        {MapPointResource.CHEST: [MapCoordinateModel(X=w - 1, Y=h - 1)]})

    def test_res_out_of_map(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(SpawnPointOutOfMapError):
            MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(w)] for _ in range(h)],
                        {MapPointResource.CHEST: [MapCoordinateModel(X=w, Y=h)]})

    def test_no_player(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(NoPlayerSpawnPointError):
            MapTemplate(w, h, [[MapPointStatus.EMPTY for _ in range(w)] for _ in range(h)],
                        {MapPointResource.CHEST: [MapCoordinateModel(X=w, Y=h)]})

    def test_parse_file(self):
        mt = MapTemplate.load_from_file("tests/res/map/map")

        self.assertEqual(mt.width, 9)
        self.assertEqual(mt.height, 9)
        self.assertEqual(
            mt.points,
            [
                [MapPointStatus.EMPTY] * 5
                + [MapPointStatus.PLAYER]
                + [MapPointStatus.CHEST]
                + [MapPointStatus.MONSTER]
                + [MapPointStatus.FIELD_BOSS]
            ] * 9
        )
        self.assertEqual(
            mt.resources,
            {
                MapPointResource.CHEST: [MapCoordinateModel(X=3, Y=y) for y in range(1, 4)],
                MapPointResource.MONSTER: [MapCoordinateModel(X=4, Y=y) for y in range(1, 4)],
                MapPointResource.FIELD_BOSS: [MapCoordinateModel(X=5, Y=y) for y in range(1, 4)]
            }
        )

    def test_parse_file_unspawnable(self):
        with self.assertRaises(MapPointUnspawnableError):
            MapTemplate.load_from_file("tests/res/map/map_unspawnable")

    def test_parse_file_res_out_of_map(self):
        with self.assertRaises(SpawnPointOutOfMapError):
            MapTemplate.load_from_file("tests/res/map/map_outofmap")

    def test_parse_file_unknown_resource(self):
        with self.assertRaises(UnknownResourceTypeError):
            MapTemplate.load_from_file("tests/res/map/map_resource")

    def test_parse_file_no_player(self):
        with self.assertRaises(NoPlayerSpawnPointError):
            MapTemplate.load_from_file("tests/res/map/map_noplayer")
