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
    QgsVectorLayer,
    QgsWkbTypes,
)

from morphal.ptm4qgis_algorithm import PTM4QgisAlgorithm

from . import morphal_geometry_utils as geometry_utils
from .utils import LayerRenamer


class MorphALGeometryToSegments(PTM4QgisAlgorithm):
    INPUT_LAYER = "INPUT_LAYER"
    UNICITY = "UNICITY"
    OUTPUT_LAYER = "OUTPUT_LAYER"

    def help(self):
        return self.tr(
            "Geometry to segments. Transform a layer of lines or polygons into segments."
        )

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
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
                self.OUTPUT_LAYER, self.tr("Segments"), QgsProcessing.TypeVectorLine
            )
        )

    def name(self):
        return "geometry_to_segments"

    def displayName(self):
        return self.tr("Geometry to segments")

    def processAlgorithm(self, parameters, context, feedback):
        # input / source
        source = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT_LAYER)
            )

        wkb_type = source.wkbType()

        if (
            QgsWkbTypes.geometryType(wkb_type) != QgsWkbTypes.PolygonGeometry
            and QgsWkbTypes.geometryType(wkb_type) != QgsWkbTypes.LineGeometry
        ):
            feedback.reportError(
                self.tr("The layer geometry type is different from a line or a polygon")
            )
            return {}

        if source.featureCount() == 0:
            feedback.reportError(
                self.tr("The layer doesn't contain any feature: no output provided")
            )
            return {}

        source_layer = self.parameterAsLayer(parameters, self.INPUT_LAYER, context)

        # other parameters
        unicity = self.parameterAsBoolean(parameters, self.UNICITY, context)

        # output
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_LAYER,
            context,
            source.fields(),
            QgsWkbTypes.LineString,
            source.sourceCrs(),
        )
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT_LAYER))

        # process
        vector_layer = QgsVectorLayer("LineString", "temp", "memory")

        dp = vector_layer.dataProvider()
        dp.addAttributes(source.fields())
        vector_layer.updateFields()

        vector_layer.startEditing()

        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        if QgsWkbTypes.geometryType(wkb_type) == QgsWkbTypes.PolygonGeometry:
            for current, f in enumerate(features):
                if feedback.isCanceled():
                    return {}

                if not f.hasGeometry():
                    continue
                else:
                    for p in self.polygon_to_segments(f.geometry()):
                        feat = QgsFeature()
                        feat.setAttributes(f.attributes())
                        feat.setGeometry(p)
                        vector_layer.addFeature(feat, QgsFeatureSink.FastInsert)

                feedback.setProgress(int(current * total))
        else:  # LineGeometry
            for current, f in enumerate(features):
                if feedback.isCanceled():
                    return {}

                if not f.hasGeometry():
                    continue
                else:
                    for p in self.line_to_segments(f.geometry()):
                        feat = QgsFeature()
                        feat.setAttributes(f.attributes())
                        feat.setGeometry(p)
                        vector_layer.addFeature(feat, QgsFeatureSink.FastInsert)

                feedback.setProgress(int(current * total))

        vector_layer.commitChanges()

        if unicity:
            alg_params = {
                'INPUT': vector_layer,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }

            layer_with_deleted_duplicate_geom = processing.run(
                "native:deleteduplicategeometries",
                alg_params,
                context=context,
                feedback=feedback,
                is_child_algorithm=True
            )

            vlyr = context.getMapLayer(layer_with_deleted_duplicate_geom['OUTPUT'])

            for f in vlyr.getFeatures():
                sink.addFeature(f, QgsFeatureSink.FastInsert)
        else:
            for f in vector_layer.getFeatures():
                sink.addFeature(f, QgsFeatureSink.FastInsert)

        # rename output layer
        global segments_renamer

        segments_newname = ""
        segments_newname = '{}-Segments'.format(
            source_layer.name()
        )

        if unicity:
            segments_newname += self.tr("-Unicity")

        segments_renamer = LayerRenamer(segments_newname)
        context.layerToLoadOnCompletionDetails(
            dest_id).setPostProcessor(segments_renamer)

        return {self.OUTPUT_LAYER: dest_id}

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

                        segment = geometry_utils.create_normalized_segment(p1, p2)
                        segment_wkt = segment.asWkt()

                        if segment_wkt not in all_segments:
                            all_segments.append(segment_wkt)
                            segments.append(segment)
            else:
                line = boundary.asPolyline()
                for i in range(len(line) - 1):
                    p1 = QgsPoint(line[i])
                    p2 = QgsPoint(line[i + 1])

                    segment = geometry_utils.create_normalized_segment(p1, p2)
                    segment_wkt = segment.asWkt()

                    if segment_wkt not in all_segments:
                        all_segments.append(segment_wkt)
                        segments.append(segment)

        return segments

    def polygon_to_segments(self, geometry):
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

                        segment = geometry_utils.create_normalized_segment(p1, p2)
                        segments.append(segment)
            else:
                line = boundary.asPolyline()
                for i in range(len(line) - 1):
                    p1 = QgsPoint(line[i])
                    p2 = QgsPoint(line[i + 1])

                    segment = geometry_utils.create_normalized_segment(p1, p2)
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

                        segment = geometry_utils.create_normalized_segment(p1, p2)
                        segment_wkt = segment.asWkt()

                        if segment_wkt not in all_segments:
                            all_segments.append(segment_wkt)
                            segments.append(segment)
            else:
                line = geom.asPolyline()
                for i in range(len(line) - 1):
                    p1 = QgsPoint(line[i])
                    p2 = QgsPoint(line[i + 1])

                    segment = geometry_utils.create_normalized_segment(p1, p2)
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

                        segment = geometry_utils.create_normalized_segment(p1, p2)
                        segments.append(segment)
            else:
                line = geom.asPolyline()
                for i in range(len(line) - 1):
                    p1 = QgsPoint(line[i])
                    p2 = QgsPoint(line[i + 1])

                    segment = geometry_utils.create_normalized_segment(p1, p2)
                    segments.append(segment)
        return segments
