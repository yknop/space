from unittest.mock import patch, call
import pytest

from modules.polygon import (
    create_polygon,
    combine_all_polygons,
    convert_square_to_polygon,
    polygon_object,
    polygon_arrangement,
    remove_unnecessary_points,
    multi_polygon_object,
    multi_polygon_arrangement,
)


class MockMultiPolygon:
    def __init__(self, polygons):
        self.geoms = polygons


class MockPolygon:
    def __init__(self, geom_type, coords_exterior="", coords_interiors=""):
        self.geom_type = geom_type
        self.exterior = MockExterior(coords_exterior)
        self.interiors = [MockInteriors(coords_interiors)]


class MockExterior:
    def __init__(self, coords):
        self.coords = coords


class MockInteriors:
    def __init__(self, coords):
        self.coords = coords


class MockCombinedPolygon:
    def __init__(self, result_union=""):
        self.result_union = result_union

    def union(self, polygon):
        return self.result_union


@patch("modules.polygon.combine_all_polygons")
@patch(
    "modules.polygon.polygon_object",
    return_value="return from polygon_object",
)
@patch(
    "modules.polygon.multi_polygon_object",
    return_value="return from multi_polygon_object",
)
def test_create_polygon_when_combine_all_polygons_return_polygon(
    mock_multi_polygon_object,
    mock_polygon_object,
    mock_combine_all_polygons,
):
    mock_polygon = MockPolygon(
        "Polygon", [(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]
    )
    mock_combine_all_polygons.return_value = mock_polygon
    squares = [[(0, 0), (100, 100)], [(50, 50), (70, 70)]]
    assert create_polygon(squares) == "return from polygon_object"
    mock_combine_all_polygons.assert_called_once_with(squares)
    mock_polygon_object.assert_called_once_with(mock_polygon)
    mock_multi_polygon_object.assert_not_called()


@patch("modules.polygon.combine_all_polygons")
@patch(
    "modules.polygon.polygon_object",
    return_value="return from polygon_object",
)
@patch(
    "modules.polygon.multi_polygon_object",
    return_value="return from multi_polygon_object",
)
def test_create_polygon_when_combine_all_polygons_return_multi_polygon(
    mock_multi_polygon_object,
    mock_polygon_object,
    mock_combine_all_polygons,
):
    mock_polygon = MockPolygon(
        "MultiPolygon",
        [
            [(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)],
            [(1000, 1000), (1000, 2000), (2000, 2000), (2000, 1000), (1000, 1000)],
        ],
    )
    mock_combine_all_polygons.return_value = mock_polygon
    assert (
        create_polygon([[(0, 0), (100, 100)], [(1000, 1000), (2000, 2000)]])
        == "return from multi_polygon_object"
    )
    mock_combine_all_polygons.assert_called_once_with(
        [[(0, 0), (100, 100)], [(1000, 1000), (2000, 2000)]]
    )
    mock_polygon_object.assert_not_called()
    mock_multi_polygon_object.assert_called_once_with(mock_polygon)


@patch(
    "modules.polygon.combine_all_polygons",
    return_value=MockPolygon("GeometryCollection"),
)
@patch(
    "modules.polygon.polygon_object",
    return_value="return from polygon_object",
)
@patch(
    "modules.polygon.multi_polygon_object",
    return_value="return from multi_polygon_object",
)
def test_create_polygon_when_combine_all_polygons_return_other_geometry_collection(
    mock_multi_polygon_object,
    mock_polygon_object,
    mock_combine_all_polygons,
):
    with pytest.raises(Exception) as exception:
        create_polygon([[(100, 0), (50, 60)], [(100, 30), (50, 60)], [(50, 3), (5, 3)]])
    assert str(exception.value) == "The squares are not divided correctly"
    mock_combine_all_polygons.assert_called_once_with(
        [[(100, 0), (50, 60)], [(100, 30), (50, 60)], [(50, 3), (5, 3)]]
    )
    mock_polygon_object.assert_not_called()
    mock_multi_polygon_object.assert_not_called()


@patch("modules.polygon.convert_square_to_polygon")
def test_combine_all_polygons(mock_convert_square_to_polygon):
    mock_convert_square_to_polygon.side_effect = [
        MockCombinedPolygon("result_polygon"),
        MockCombinedPolygon(),
    ]
    assert (
        combine_all_polygons([[(0, 0), (100, 100)], [(1000, 1000), (2000, 2000)]])
        == "result_polygon"
    )
    assert mock_convert_square_to_polygon.call_count == 2
    mock_convert_square_to_polygon.assert_has_calls(
        [call([(0, 0), (100, 100)]), call([(1000, 1000), (2000, 2000)])]
    )


@patch("modules.polygon.Polygon", return_value="Polygon")
def test_convert_square_to_polygon(mock_polygon):
    assert convert_square_to_polygon([(0, 0), (100, 100)]) == "Polygon"
    mock_polygon.assert_called_once_with([(0, 0), (0, 100), (100, 100), (100, 0)])


@patch(
    "modules.polygon.polygon_arrangement",
    return_value=[
        [(3.0, 2.0), (3.0, 0.0), (0.0, 0.0), (0.0, 3.0), (3.0, 3.0), (3.0, 2.0)],
        [(2.0, 2.0), (1.0, 2.0), (1.0, 1.0), (2.0, 1.0), (2.0, 2.0)],
    ],
)
def test_polygon_object(mock_polygon_arrangement):
    mock_polygon = MockPolygon("Polygon")
    assert polygon_object(mock_polygon) == {
        "type": "Polygon",
        "coordinates": [
            [(3.0, 2.0), (3.0, 0.0), (0.0, 0.0), (0.0, 3.0), (3.0, 3.0), (3.0, 2.0)],
            [(2.0, 2.0), (1.0, 2.0), (1.0, 1.0), (2.0, 1.0), (2.0, 2.0)],
        ],
    }
    mock_polygon_arrangement.assert_called_once_with(mock_polygon)


@patch(
    "modules.polygon.remove_unnecessary_points",
    return_value=[
        (3.0, 2.0),
        (3.0, 0.0),
        (0.0, 0.0),
        (0.0, 3.0),
        (3.0, 3.0),
        (3.0, 2.0),
    ],
)
def test_polygon_arrangement(mock_remove_unnecessary_points):
    mock_polygon = MockPolygon(
        "Polygon",
        [
            (3.0, 2.0),
            (3.0, 0.0),
            (2.0, 0.0),
            (0.0, 0.0),
            (0.0, 3.0),
            (3.0, 3.0),
            (3.0, 2.0),
        ],
        [(2.0, 2.0), (1.0, 2.0), (1.0, 1.0), (2.0, 1.0), (2.0, 2.0)],
    )
    assert polygon_arrangement(mock_polygon) == [
        [(3.0, 2.0), (3.0, 0.0), (0.0, 0.0), (0.0, 3.0), (3.0, 3.0), (3.0, 2.0)],
        [(2.0, 2.0), (1.0, 2.0), (1.0, 1.0), (2.0, 1.0), (2.0, 2.0)],
    ]
    mock_remove_unnecessary_points.assert_called_once_with(
        [
            (3.0, 2.0),
            (3.0, 0.0),
            (2.0, 0.0),
            (0.0, 0.0),
            (0.0, 3.0),
            (3.0, 3.0),
            (3.0, 2.0),
        ]
    )


def test_remove_unnecessary_points():
    assert remove_unnecessary_points(
        [
            (210.0, 0.0),
            (105.0, 0.0),
            (0.0, 0.0),
            (0.0, 100.0),
            (0.0, 200.0),
            (0.0, 300.0),
            (0.0, 400.0),
            (0.0, 500.0),
            (0.0, 600.0),
            (105.0, 600.0),
            (105.0, 500.0),
            (105.0, 400.0),
            (210.0, 400.0),
            (210.0, 300.0),
            (210.0, 200.0),
            (210.0, 100.0),
            (315.0, 100.0),
            (315.0, 0.0),
            (210.0, 0.0),
        ]
    ) == [
        (210.0, 0.0),
        (0.0, 0.0),
        (0.0, 600.0),
        (105.0, 600.0),
        (105.0, 400.0),
        (210.0, 400.0),
        (210.0, 100.0),
        (315.0, 100.0),
        (315.0, 0.0),
        (210.0, 0.0),
    ]


@patch(
    "modules.polygon.multi_polygon_arrangement",
    return_value="return from multi_polygon_arrangement",
)
def test_multi_polygon_object(mock_multi_polygon_arrangement):
    assert multi_polygon_object("multi_polygon") == {
        "type": "MultiPolygon",
        "coordinates": "return from multi_polygon_arrangement",
    }
    mock_multi_polygon_arrangement.assert_called_once_with("multi_polygon")


@patch(
    "modules.polygon.polygon_arrangement",
    return_value="return from polygon_arrangement",
)
def test_multi_polygon_arrangement(mock_polygon_arrangement):
    mock_polygon_example_1 = MockPolygon(
        "Polygon", [(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]
    )
    mock_polygon_example_2 = MockPolygon(
        "Polygon",
        [(100, 100), (100, 10000), (10000, 10000), (10000, 100), (100, 100)],
    )
    assert multi_polygon_arrangement(
        MockMultiPolygon([mock_polygon_example_1, mock_polygon_example_2])
    ) == ["return from polygon_arrangement", "return from polygon_arrangement"]
    assert mock_polygon_arrangement.call_count == 2
    mock_polygon_arrangement.assert_has_calls(
        [call(mock_polygon_example_1), call(mock_polygon_example_2)]
    )
