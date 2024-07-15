# -*- coding: utf-8 -*-
"""
/***************************************************************************
    MorphAL: PTM plugin for QGIS
    --------------
    Start date           : January 2021
    Copyright            : (C) 2021, Eric Grosso, PTM
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import math

from qgis.core import QgsDistanceArea, QgsGeometry, QgsLineString, QgsPoint, QgsPolygon

from .utils import round_down_float_to_3_decimals


def points_comparison(
        point_0: QgsPoint,
        point_1: QgsPoint
):
    if point_0.x() < point_1.x():
        return -1
    if point_0.x() > point_1.x():
        return 1
    if point_0.y() < point_1.y():
        return -1
    if point_0.y() > point_1.y():
        return 1
    return 0


def create_normalized_segment(
        point_0: QgsPoint,
        point_1: QgsPoint
):
    if points_comparison(point_0, point_1) < 0:
        return QgsGeometry(QgsLineString([point_0, point_1]))
    return QgsGeometry(QgsLineString([point_1, point_0]))


def polygon_orientation(polygon: QgsPolygon):
    """
    Compute the orientation of a polygon (QgsPolygon) (in degrees)
    comparatively to the cartographic East (axis X).
    The orientation is based on the orientation of the associated minimum
    bounding rectangle. Its value is between 0 and 180 degrees, except if
    the MBR can not be defined. In that last case, the value -2.0 is returned.
    """
    # orientedMinimumBoundingBox(self) → Tuple[QgsGeometry, float, float, float, float]
    # angle (clockwise in degrees from North)
    (mbr, area, angle, width, height) = polygon.orientedMinimumBoundingBox()
    if mbr.isNull() or mbr.isEmpty():
        return -2.0

    # geom = mbr.geometry()
    v0 = QgsPoint(mbr[0])
    v1 = QgsPoint(mbr[1])
    v2 = QgsPoint(mbr[2])

    length = v0.distanceSquared(v1.x(), v1.y())
    length2 = v1.distanceSquared(v2.x(), v2.y())

    if length > length2:
        angle = math.atan2(v0.y() - v1.y(), v0.x() - v1.x())
    else:
        angle = math.atan2(v1.y() - v2.y(), v1.x() - v2.x())

    if angle < 0:
        angle += math.pi

    return angle * 180.0 / math.pi

    # for v in mbr.vertices():
    #     print(v.x(), v.y())
    # line = mbr.asPolyline()

    # for i in range(len(line) - 1):
    #     p1 = QgsPoint(line[i])
    #     p2 = QgsPoint(line[i + 1])

    #
    # # QgsGeometry = polygon.convexHull()
    # convex_hull = polygon.convexHull()
    # if convex_hull is null:
    #     return -2.0


def _mbr_orientation(mbr: QgsPolygon):
    """
    Compute the orientation of a minimum bounding rectangle (QgsPolygon)
    (in degrees) comparatively to the cartographic East (axis X).
    Its value is between 0 and 180 degrees.
    """
    # , except if the MBR is geometrically
    # null or empty. In that last case, the value -2.0 is returned.
    # if mbr.isNull() or mbr.isEmpty():
    #     return -2.0

    # geom = mbr.geometry()

    mbr_vertices = _geometry_vertices(mbr, 2)
    v0 = QgsPoint(mbr_vertices[0].x(), mbr_vertices[0].y())
    v1 = QgsPoint(mbr_vertices[1].x(), mbr_vertices[1].y())
    v2 = QgsPoint(mbr_vertices[2].x(), mbr_vertices[2].y())

    length = v0.distanceSquared(v1.x(), v1.y())
    length2 = v1.distanceSquared(v2.x(), v2.y())

    if length > length2:
        angle_x = math.atan2(v0.y() - v1.y(), v0.x() - v1.x())
    else:
        angle_x = math.atan2(v1.y() - v2.y(), v1.x() - v2.x())

    if angle_x < 0:
        angle_x += math.pi

    return angle_x * 180.0 / math.pi


def _geometry_vertices(
        geometry: QgsGeometry,
        index: int
):
    vertices = []
    if index < 0:
        return vertices

    i = 0
    for v in geometry.vertices():
        vertices.append(v)

        if i == index:
            return vertices

        i += 1


def _geometry_num_vertices(geometry: QgsGeometry):
    if geometry.isNull() or geometry.isEmpty():
        return 0

    index = 0
    for v in geometry.vertices():
        index += 1

    return index


def rectangle_elongation(polygon: QgsPolygon):
    """
    Compute the elongation of a rectangle, equals to the ratio length / width.
    If the polygon in parameter has a number of coordinates different from 5,
    the value -1.0 is returned.
    """

    if _geometry_num_vertices(polygon) != 5:
        return -1.0

    vertices = _geometry_vertices(polygon, 2)

    v0 = QgsPoint(vertices[0].x(), vertices[0].y())
    v1 = QgsPoint(vertices[1].x(), vertices[1].y())
    v2 = QgsPoint(vertices[2].x(), vertices[2].y())

    length = v0.distance(v1.x(), v1.y())
    length2 = v1.distance(v2.x(), v2.y())

    if length >= length2:
        return length / length2
    return length2 / length


def is_circle(
    polygon: QgsPolygon,
    miller_index_threshold: float,
    distance_area: QgsDistanceArea
):
    """
    Compute if a polygon (QgsPolygon) has a circular shape or not, based on
    the compactness index or Miller's index (if Miller's index equals 1,
    it means that the shape is a perfect circle). iMillerThreshold is the
    minimum threshold for Miller's index. Returns true if the polygon shape
    is a circle, false otherwise.
    """

    if compactness_miller_index(polygon, distance_area) >= miller_index_threshold:
        return True

    return False


def compactness_miller_index(
        polygon: QgsPolygon,
        distance_area: QgsDistanceArea
):
    """
    Compute the compactness index of a polygon (QgsPolygon),
    based on Miller's index, 4.Pi.area / perimeter^2.
    """

    # TODO ? test if geometry is null / empty ?
    if _geometry_num_vertices(polygon) < 4:
        return 0.0

    perimeter = distance_area.measurePerimeter(polygon)
    if perimeter == 0:
        return 0.0
    area = distance_area.measureArea(polygon)
    return 4 * math.pi * area / math.pow(perimeter, 2)


def compactness_gravelius_index(
        polygon: QgsPolygon,
        distance_area: QgsDistanceArea
):
    """
    Compute the compactness index of a polygon (QgsPolygon),
    based on Gravelius' index, perimeter / 2.sqrt(Pi.area)
    """

    # TODO ? test if geometry is null / empty ?
    if _geometry_num_vertices(polygon) < 4:
        return 0.0

    perimeter = distance_area.measurePerimeter(polygon)
    area = distance_area.measureArea(polygon)

    if perimeter == 0 or area == 0:
        return 0.0
    return perimeter / (2 * math.sqrt(math.pi * area))


def is_rectangle(
    polygon: QgsPolygon,
    sd_convex_hull_threshold: float,
    sd_mbr_threshold: float,
    distance_area: QgsDistanceArea,
):
    """
    Compute if a Polygon has a rectangular shape or not, based on the comparison
    with two shapes: the shape of the minimum bounding rectangle of the Polygon,
    and the shape of the convex hull associated to the Polygon. This comparison
    is computed thanks to two thresholds (threshold of maximums), one for each associated
    shape. If the shape is rectangular, the orientation (in degrees) based on the is returned;
    otherwise, the value of -1.0 is returned. Finally, if the returned value equals -2.0,
    it means that the MBR can not be computed.

    :param polygon: polygon to process
    :param sd_convex_hull_threshold: maximum threshold for surface distance between the polygon and its convex hull
    :param sd_mbr_threshold: maximum threshold for surface distance between the polygon and its associated minimum bounding rectangle
    :return: the orientation in degrees of the polygon, based on the orientation of the associated minimum bounding rectangle,
    -1.0 if the polygon shape is not defined as a rectangle, and -2.0 if the convex hull or MBR can not be computed
    """

    convex_hull = polygon.convexHull()
    if convex_hull.isNull() or convex_hull.isEmpty():
        return -2.0

    # orientedMinimumBoundingBox(self) → Tuple[QgsGeometry, float, float, float, float]
    # angle (clockwise in degrees from North)
    (mbr, area, angle, width, height) = polygon.orientedMinimumBoundingBox()
    if mbr.isNull() or mbr.isEmpty():
        return -2.0

    sd_convex_hull = surface_distance(polygon, convex_hull, distance_area)
    sd_mbr = surface_distance(polygon, mbr, distance_area)

    if sd_convex_hull <= sd_convex_hull_threshold and sd_mbr <= sd_mbr_threshold:
        return _mbr_orientation(mbr)

    return -1.0


def is_rectangle_indices(
        polygon: QgsPolygon,
        distance_area: QgsDistanceArea
):
    """
    Compute if a polygon has a rectangular shape or not, based on the comparison
    with two shapes: the shape of the minimum bounding rectangle of the polygon,
    and the shape of the convex hull associated to the polygon. This comparison
    is computed thanks to two thresholds (threshold of maximums), one for each associated
    shape. If the shape is rectangular, the orientation (in degrees) based on the is returned;
    otherwise, the value of -1.0 is returned. Finally, if the returned value equals -2.0,
    it means that the MBR can not be computed.

    :param QgsPolygon polygon: polygon to process
    :param QgsDistanceArea distance_area: distance area
    :return:
      - the surface distance between the polygon and its convex hull,
      - the surface distance between the polygon and its associated minimum bounding rectangle,
      - the orientation in degrees of the polygon, based on the orientation of the associated minimum bounding rectangle,
      -1.0 if the polygon shape is not defined as a rectangle, and -2.0 if the convex hull or MBR can not be computed
    """

    sd_convex_hull = -2.0
    sd_mbr = -2.0
    mbr_orientation = -1.0

    convex_hull = polygon.convexHull()
    if convex_hull.isNull() or convex_hull.isEmpty():
        sd_convex_hull = -2.0
    else:
        sd_convex_hull = surface_distance(polygon, convex_hull, distance_area)

    # orientedMinimumBoundingBox(self) → Tuple[QgsGeometry, float, float, float, float]
    # angle (clockwise in degrees from North)
    (mbr, area, angle, width, height) = polygon.orientedMinimumBoundingBox()
    if mbr.isNull() or mbr.isEmpty():
        sd_mbr = -2.0
    else:
        sd_mbr = surface_distance(polygon, mbr, distance_area)
        mbr_orientation = _mbr_orientation(mbr)

    elongation = -1.0
    if width >= height:
        elongation = width / height
    else:
        elongation = height / width

    return sd_convex_hull, sd_mbr, mbr_orientation, elongation


def surface_distance(
    geometry_a: QgsGeometry,
    geometry_b: QgsGeometry,
    distance_area: QgsDistanceArea
):
    """
    Compute the surface distance between two geometries.
    Surface distance is a number between 0 and 1, computed thanks to
    the following formula: 1 - (area(intersection) / area(union)).

    :param QgsGeometry geometry_a: first geometry to process
    :param QgsGeometry geometry_b: second geometry to process
    :param QgsDistanceArea distance_area: distance area
    :return: the surface distance between geometry A and geometry B
    """

    intersection = geometry_a.intersection(geometry_b)
    if intersection.isNull() or intersection.isEmpty():
        return 1.0

    union = geometry_a.combine(geometry_b)
    if union.isNull() or union.isEmpty():
        return 1.0

    intersection_area = distance_area.measureArea(intersection)
    union_area = distance_area.measureArea(union)

    return 1 - intersection_area / union_area


def angle(
        geometry: QgsGeometry,
        unit: int,
        interval: float,
        accuracy: bool
):
    """
    Compute the angle between 2 points (between 0 and PI or between O and PI/2)
    comparatively to the X axis.

    geometry --> check

    :param QgsGeometry geometry: geometry to process
    :param int unit: unit in degree if 0, grade if 2 (radian if something else)
    :param float interval: interval [ 0 ; PI [ if 0, [ 0 ; PI/2 [ if 1,
                    otherwise the interval [ 0 ; PI/2 [ is the default choice
    :param bool accuracy: true to keep two numbers after the dot, false to keep all numbers
    :return: the computed angle or None otherwise
    """

    num_vertices = _geometry_num_vertices(geometry)
    if num_vertices != 2:  # includes null or empty geometries
        return None

    vertices = _geometry_vertices(geometry, 1)
    v0 = QgsPoint(vertices[0].x(), vertices[0].y())
    v1 = QgsPoint(vertices[1].x(), vertices[1].y())

    x = v1.x() - v0.x()
    y = v1.y() - v0.y()
    angle_x = math.atan2(y, x)

    #  [O ; Pi[
    if interval == 0:
        if angle_x < 0:
            angle_x = angle_x + math.pi
        if angle_x == math.pi:
            angle_x = 0.0
    else:  # [O ; Pi/2[
        if angle_x < 0:
            angle_x = angle_x + math.pi
        angle_x = angle_x % (math.pi / 2.0)
        if angle_x == (math.pi / 2.0):
            angle_x = 0.0

    # unit conversion
    if unit == 0:  # degree
        angle_x = math.degrees(angle_x)
    elif unit == 2:  # grade
        angle_x = angle_x * 200.0 / math.pi

    # accuracy
    if accuracy:
        angle_x = round_down_float_to_3_decimals(angle_x)

    return angle_x
