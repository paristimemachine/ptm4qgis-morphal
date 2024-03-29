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


def points_comparison(p1: QgsPoint, p2: QgsPoint):
    if p1.x() < p2.x():
        return -1
    if p1.x() > p2.x():
        return 1
    if p1.y() < p2.y():
        return -1
    if p1.y() > p2.y():
        return 1
    return 0


def create_normalized_segment(p1: QgsPoint, p2: QgsPoint):
    if points_comparison(p1, p2) < 0:
        return QgsGeometry(QgsLineString([p2, p1]))
    else:
        return QgsGeometry(QgsLineString([p1, p2]))


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
        angle = math.atan2(v0.y() - v1.y(), v0.x() - v1.x())
    else:
        angle = math.atan2(v1.y() - v2.y(), v1.x() - v2.x())

    if angle < 0:
        angle += math.pi

    return angle * 180.0 / math.pi


def _geometry_vertices(geometry: QgsGeometry, index: int):
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


def polygon_elongation(polygon: QgsPolygon):
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

    if length == length2:
        return length / length2
    return length2 / length


def is_circle(
    polygon: QgsPolygon, i_miller_threshold: float, distance_area: QgsDistanceArea
):
    """
    Compute if a polygon (QgsPolygon) has a circular shape or not, based on
    the compactedness index or Miller's index (if Miller's index equals 1,
    it means that the shape is a perfect circle). iMillerThreshold is the
    minimum threshold for Miller's index. Returns true if the polygon shape
    is a circle, false otherwise.
    """

    if compactedness_index(polygon, distance_area) >= i_miller_threshold:
        return True

    return False


def compactedness_index(polygon: QgsPolygon, distance_area: QgsDistanceArea):
    """
        Compute the compactedness index of a polygon (QgsPolygon),
    i.e. Miller's index, 4.Pi.area / perimeter^2.
    """

    # TODO ? test if geometry is null / empty ?
    if _geometry_num_vertices(polygon) < 4:
        return 0.0

    perimeter = distance_area.measurePerimeter(polygon)
    if perimeter == 0:
        return 0.0
    area = distance_area.measureArea(polygon)
    return 4 * math.pi * area / math.pow(perimeter, 2)


def is_rectangle(
    polygon: QgsPolygon,
    sd_convex_hull_threshold: float,
    sd_mbr_threshold: float,
    distance_area: QgsDistanceArea,
):
    """
    Compute if a {@link Polygon} has a rectangular shape or not, based on the comparison
    with two shapes: the shape of the minimum bounding rectangle of the {@link Polygon},
    and the shape of the convex hull associated to the {@link Polygon}. This comparison
    is computed thanks to two thresholds (threshold of maximums), one for each associated
    shape. If the shape is rectangular, the orientation (in degrees) based on the is returned;
    otherwise, the value of -1.0 is returned. Finally, if the returned value equals -2.0,
    it means that the MBR can not be computed.

    @param polygon polygon to process
    @param sd_convex_hull_threshold maximum threshold for surface distance between the polygon and its convex hull
    @param sd_mbr_threshold maximum threshold for surface distance between the polygon and its associated minimum bounding rectangle
    @return the orientation in degrees of the polygon, based on the orientation of the associated minimum bounding rectangle,
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


def is_rectangle_indices(polygon: QgsPolygon, distance_area: QgsDistanceArea):
    """
    Compute if a {@link Polygon} has a rectangular shape or not, based on the comparison
    with two shapes: the shape of the minimum bounding rectangle of the {@link Polygon},
    and the shape of the convex hull associated to the {@link Polygon}. This comparison
    is computed thanks to two thresholds (threshold of maximums), one for each associated
    shape. If the shape is rectangular, the orientation (in degrees) based on the is returned;
    otherwise, the value of -1.0 is returned. Finally, if the returned value equals -2.0,
    it means that the MBR can not be computed.

    @param polygon polygon to process
    @param sd_convex_hull_threshold maximum threshold for surface distance between the polygon and its convex hull
    @param sd_mbr_threshold maximum threshold for surface distance between the polygon and its associated minimum bounding rectangle
    @return the orientation in degrees of the polygon, based on the orientation of the associated minimum bounding rectangle,
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

    return sd_convex_hull, sd_mbr, mbr_orientation


def surface_distance(
    geometry_a: QgsGeometry, geometry_b: QgsGeometry, distance_area: QgsDistanceArea
):
    """
    Compute the surface distance between two {@link Geometry}s.
    Surface distance is a number between 0 and 1, computed thanks to
    the following formula: 1 - (area(intersection) / area(union)).

    @param geometryA first geometry to process
    @param geometryB second geometry to process
    @return the surface distance between geometry A and geometry B
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


def angle(geometry: QgsGeometry, unit: int, interval: float, accuracy: bool):
    """
    Compute the angle between 2 {@link Point}s (between 0 and PI or between O and PI/2)
    comparatively to the X axis.

    geometry --> check

        @param unit unit in degree if 0, grade if 2 (radian if something else)
        @param interval interval [ 0 ; PI [ if 0, [ 0 ; PI/2 [ if 1,
                        otherwise the interval [ 0 ; PI/2 [ is the default choice
        @param accuracy true to keep two numbers after the dot, false to keep all numbers
        @return the computed angle or None otherwise
    """

    num_vertices = _geometry_num_vertices(geometry)
    if num_vertices == 0:  # null or empty
        return None

    if num_vertices != 2:
        return None
    else:
        vertices = _geometry_vertices(geometry, 1)
        v0 = QgsPoint(vertices[0].x(), vertices[0].y())
        v1 = QgsPoint(vertices[1].x(), vertices[1].y())

        x = v1.x() - v0.x()
        y = v1.y() - v0.y()
        angle = math.atan2(y, x)

        #  [O ; Pi[
        if interval == 0:
            if angle < 0:
                angle = angle + math.pi
            if angle == math.pi:
                angle = 0.0
        else:  # [O ; Pi/2[
            if angle < 0:
                angle = angle + math.pi
            angle = angle % (math.pi / 2.0)
            if angle == (math.pi / 2.0):
                angle = 0.0

        # unit conversion
        if unit == 0:  # degree
            angle = math.degrees(angle)
        elif unit == 2:  # grade
            angle = angle * 200.0 / math.pi

        # accuracy
        if accuracy:
            angle = round(angle, 3)

        return angle
