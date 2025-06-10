from typing import Any, Dict, List, Tuple, Union

from shapely.geometry import MultiPolygon, Polygon


def create_polygon(
    squares: List[Tuple[Tuple[int, int], Tuple[int, int]]],
) -> Dict[str, Any]:
    polygons = combine_all_polygons(squares)
    match polygons.geom_type:
        case "Polygon":
            return polygon_object(polygons)
        case "MultiPolygon":
            return multi_polygon_object(polygons)
        case _:
            raise Exception("The squares are not divided correctly")


def combine_all_polygons(
    squares: List[Tuple[Tuple[int, int], Tuple[int, int]]],
) -> Union[Polygon, MultiPolygon]:
    combined_polygon = convert_square_to_polygon(squares[0])
    for square in squares[1:]:
        polygon = convert_square_to_polygon(square)
        combined_polygon = combined_polygon.union(polygon)
    return combined_polygon


def convert_square_to_polygon(
    square: Tuple[Tuple[int, int], Tuple[int, int]],
) -> Polygon:
    x1, y1 = square[0]
    x2, y2 = square[1]
    return Polygon([(x1, y1), (x1, y2), (x2, y2), (x2, y1)])


def polygon_object(polygon: Polygon) -> Dict[str, Any]:
    return {"type": "Polygon", "coordinates": polygon_arrangement(polygon)}


def polygon_arrangement(polygon: Polygon) -> List[List[Tuple[float, float]]]:
    polygon_coordinates = [remove_unnecessary_points(list(polygon.exterior.coords))]
    for item in polygon.interiors:
        polygon_coordinates.append(list(item.coords))
    return polygon_coordinates


def remove_unnecessary_points(
    polygon: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    index = 1
    while index < (len(polygon) - 1):
        for i in range(2):
            if (
                polygon[index][i] == polygon[index - 1][i]
                and polygon[index][i] == polygon[index + 1][i]
            ):
                polygon.pop(index)
                index -= 1
                break
        index += 1
    return polygon


def multi_polygon_object(multi_polygon: MultiPolygon) -> Dict[str, Any]:
    return {
        "type": "MultiPolygon",
        "coordinates": multi_polygon_arrangement(multi_polygon),
    }


def multi_polygon_arrangement(
    multi_polygon: MultiPolygon,
) -> List[List[List[Tuple[float, float]]]]:
    multi_polygon_coordinates = []
    for polygon in multi_polygon.geoms:
        multi_polygon_coordinates.append(polygon_arrangement(polygon))
    return multi_polygon_coordinates
