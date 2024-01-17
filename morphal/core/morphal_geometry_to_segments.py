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

from qgis.core import (
    QgsFeature,
    QgsFeatureSink,
    QgsGeometry,
    QgsPoint,
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsWkbTypes,
)

from ..ptm4qgis_algorithm import PTM4QgisAlgorithm
from .morphal_geometry_utils import *


class MorphALGeometryToSegments(PTM4QgisAlgorithm):
    INPUT = "INPUT"
    UNICITY = "UNICITY"
    OUTPUT = "OUTPUT"

    def help(self):
        return self.tr(
            "Geometry to segments. Transform a layer of lines or polygons into segments."
        )

    def group(self):
        return self.tr("MorphAL")

    def groupId(self):
        return "morphal"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr("Input layer"),
                types=[QgsProcessing.TypeVectorLine, QgsProcessing.TypeVectorPolygon],
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.UNICITY, self.tr("Unicity of created segments"), True
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT, self.tr("Segments"), QgsProcessing.TypeVectorLine
            )
        )

    def name(self):
        return "morphalgeometrytosegments"

    def displayName(self):
        return self.tr("Geometry to segments")

    def processAlgorithm(self, parameters, context, feedback):
        unicity = self.parameterAsBoolean(parameters, self.UNICITY, context)

        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        wkb_type = source.wkbType()

        if (
            QgsWkbTypes.geometryType(wkb_type) != QgsWkbTypes.PolygonGeometry
            and QgsWkbTypes.geometryType(wkb_type) != QgsWkbTypes.LineGeometry
        ):
            feedback.reportError(
                "The layer geometry type is different from a line or a polygon"
            )
            return {}

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            QgsWkbTypes.LineString,
            source.sourceCrs(),
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        all_segments = []

        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        if QgsWkbTypes.geometryType(wkb_type) == QgsWkbTypes.PolygonGeometry:
            if unicity:
                for current, f in enumerate(features):
                    if feedback.isCanceled():
                        break

                    if not f.hasGeometry():
                        continue
                    else:
                        for p in self.polygon_to_unique_segments(
                            f.geometry(), all_segments
                        ):
                            feat = QgsFeature()
                            feat.setAttributes(f.attributes())
                            feat.setGeometry(p)
                            sink.addFeature(feat, QgsFeatureSink.FastInsert)

                    feedback.setProgress(int(current * total))
            else:
                for current, f in enumerate(features):
                    if feedback.isCanceled():
                        break

                    if not f.hasGeometry():
                        continue
                    else:
                        for p in self.polygon_to_segments(f.geometry()):
                            feat = QgsFeature()
                            feat.setAttributes(f.attributes())
                            feat.setGeometry(p)
                            sink.addFeature(feat, QgsFeatureSink.FastInsert)

                    feedback.setProgress(int(current * total))
        else:  # LineGeometry
            if unicity:
                for current, f in enumerate(features):
                    if feedback.isCanceled():
                        break

                    if not f.hasGeometry():
                        continue
                    else:
                        for p in self.line_to_unique_segments(
                            f.geometry(), all_segments
                        ):
                            feat = QgsFeature()
                            feat.setAttributes(f.attributes())
                            feat.setGeometry(p)
                            sink.addFeature(feat, QgsFeatureSink.FastInsert)

                    feedback.setProgress(int(current * total))
            else:
                for current, f in enumerate(features):
                    if feedback.isCanceled():
                        break

                    if not f.hasGeometry():
                        continue
                    else:
                        for p in self.line_to_segments(f.geometry()):
                            feat = QgsFeature()
                            feat.setAttributes(f.attributes())
                            feat.setGeometry(p)
                            sink.addFeature(feat, QgsFeatureSink.FastInsert)

                    feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def polygon_to_unique_segments(self, geometry, all_segments):
        # polygons to lines (multipart)
        boundary = QgsGeometry(geometry.constGet().boundary())
        boundaries = boundary.asGeometryCollection()

        segments = []

        for boundary in boundaries:
            if boundary.isMultipart():
                lines = boundary.asMultiPolyline()
                for line in lines:
                    for i in range(len(line) - 1):
                        p1 = QgsPoint(line[i])
                        p2 = QgsPoint(line[i + 1])

                        segment = create_normalized_segment(p1, p2)
                        segment_wkt = segment.asWkt()

                        if segment_wkt not in all_segments:
                            all_segments.append(segment_wkt)
                            segments.append(segment)
            else:
                line = boundary.asPolyline()
                for i in range(len(line) - 1):
                    p1 = QgsPoint(line[i])
                    p2 = QgsPoint(line[i + 1])

                    segment = create_normalized_segment(p1, p2)
                    segment_wkt = segment.asWkt()

                    if segment_wkt not in all_segments:
                        all_segments.append(segment_wkt)
                        segments.append(segment)

        return segments

    def polygon_to_segments(self, geometry):
        # polygons to lines (mutlipart)
        boundary = QgsGeometry(geometry.constGet().boundary())
        boundaries = boundary.asGeometryCollection()

        segments = []

        for boundary in boundaries:
            if boundary.isMultipart():
                lines = boundary.asMultiPolyline()
                for line in lines:
                    for i in range(len(line) - 1):
                        p1 = QgsPoint(line[i])
                        p2 = QgsPoint(line[i + 1])

                        segment = create_normalized_segment(p1, p2)
                        segments.append(segment)
            else:
                line = boundary.asPolyline()
                for i in range(len(line) - 1):
                    p1 = QgsPoint(line[i])
                    p2 = QgsPoint(line[i + 1])

                    segment = create_normalized_segment(p1, p2)
                    segments.append(segment)
        return segments

    def line_to_unique_segments(self, geometry, all_segments):
        collection = geometry.asGeometryCollection()

        segments = []

        for geom in collection:
            if geom.isMultipart():
                lines = geom.asMultiPolyline()
                for line in lines:
                    for i in range(len(line) - 1):
                        p1 = QgsPoint(line[i])
                        p2 = QgsPoint(line[i + 1])

                        segment = create_normalized_segment(p1, p2)
                        segment_wkt = segment.asWkt()

                        if segment_wkt not in all_segments:
                            all_segments.append(segment_wkt)
                            segments.append(segment)
            else:
                line = geom.asPolyline()
                for i in range(len(line) - 1):
                    p1 = QgsPoint(line[i])
                    p2 = QgsPoint(line[i + 1])

                    segment = create_normalized_segment(p1, p2)
                    segment_wkt = segment.asWkt()

                    if segment_wkt not in all_segments:
                        all_segments.append(segment_wkt)
                        segments.append(segment)

        return segments

    def line_to_segments(self, geometry):
        collection = geometry.asGeometryCollection()

        segments = []

        for geom in collection:
            if geom.isMultipart():
                lines = geom.asMultiPolyline()
                for line in lines:
                    for i in range(len(line) - 1):
                        p1 = QgsPoint(line[i])
                        p2 = QgsPoint(line[i + 1])

                        segment = create_normalized_segment(p1, p2)
                        segments.append(segment)
            else:
                line = geom.asPolyline()
                for i in range(len(line) - 1):
                    p1 = QgsPoint(line[i])
                    p2 = QgsPoint(line[i + 1])

                    segment = create_normalized_segment(p1, p2)
                    segments.append(segment)
        return segments
