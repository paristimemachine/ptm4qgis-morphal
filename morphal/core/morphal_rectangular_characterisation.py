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
    NULL,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingFeatureSource,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingUtils,
)
from qgis.PyQt.QtCore import QVariant

from morphal.ptm4qgis_algorithm import PTM4QgisAlgorithm

from . import morphal_geometry_utils as geometry_utils
from .utils import LayerRenamer


class MorphALRectangularCharacterisation(PTM4QgisAlgorithm):
    INPUT_LAYER = "INPUT_LAYER"

    METHOD = "CALC_METHOD"

    RECTANGLE_LEVEL_1 = "RECTANGLE_LEVEL_1"
    SD_CONVEX_RECT_1 = "SD_CONVEX_RECT_1"
    SD_MBR_RECT_1 = "SD_MBR_RECT_1"
    RECT_1_LAYER_OUTPUT = "RECT_1_LAYER_OUTPUT"
    RECT_1_COUNT = "RECT_1_COUNT"

    RECTANGLE_LEVEL_2 = "RECTANGLE_LEVEL_2"
    SD_CONVEX_RECT_2 = "SD_CONVEX_RECT_2"
    SD_MBR_RECT_2 = "SD_MBR_RECT_2"
    RECT_2_LAYER_OUTPUT = "RECT_2_LAYER_OUTPUT"
    RECT_2_COUNT = "RECT_2_COUNT"

    RECTANGLE_LEVEL_3 = "RECTANGLE_LEVEL_3"
    SD_CONVEX_RECT_3 = "SD_CONVEX_RECT_3"
    SD_MBR_RECT_3 = "SD_MBR_RECT_3"
    RECT_3_LAYER_OUTPUT = "RECT_3_LAYER_OUTPUT"
    RECT_3_COUNT = "RECT_3_COUNT"

    RECTANGULAR_GROUP = "RECTANGULAR_GROUP"
    RECTANGULAR_GROUP_LAYER_INPUT = "RECTANGULAR_GROUP_LAYER_INPUT"
    SD_CONVEX_RECT_GROUP = "SD_CONVEX_RECT_GROUP"
    SD_MBR_RECT_GROUP = "SD_MBR_RECT_GROUP"
    RECT_GROUP_LAYER_OUTPUT = "RECT_GROUP_LAYER_OUTPUT"

    CIRCULAR_SHAPE = "CIRCULAR_SHAPE"
    MILLER_INDEX = "MILLER_INDEX"
    CIRCULAR_LAYER_OUTPUT = "CIRCULAR_LAYER_OUTPUT"

    def help(self):
        return self.tr("Rectangular characterisation")

    def __init__(self):
        super().__init__()
        self.calc_methods = [
            self.tr("Layer CRS"),
            self.tr("Project CRS"),
            self.tr("Ellipsoidal"),
        ]

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                self.tr("Input layer"),
                types=[QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr("Calculate using"),
                options=self.calc_methods,
                defaultValue=0,
            )
        )

        # RECTANGLE DETECTION - LEVEL 1
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RECTANGLE_LEVEL_1,
                self.tr("Detection of rectangular shapes - Level 1"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SD_CONVEX_RECT_1,
                self.tr("Surface distance with convex hull (level 1)"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                maxValue=1.0,
                defaultValue=0.05,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SD_MBR_RECT_1,
                self.tr("Surface distance with MBR (level 1)"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                maxValue=1.0,
                defaultValue=0.05,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.RECT_1_LAYER_OUTPUT,
                self.tr("Rectangles - level 1"),
                QgsProcessing.TypeVectorAnyGeometry,
                None,
                True,
            )
        )

        # RECTANGLE DETECTION - LEVEL 2
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RECTANGLE_LEVEL_2,
                self.tr("Detection of rectangular shapes - Level 2"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SD_CONVEX_RECT_2,
                self.tr("Surface distance with convex hull (level 2)"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                maxValue=1.0,
                defaultValue=0.1,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SD_MBR_RECT_2,
                self.tr("Surface distance with MBR (level 2)"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                maxValue=1.0,
                defaultValue=0.1,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.RECT_2_LAYER_OUTPUT,
                self.tr("Rectangles - level 2"),
                QgsProcessing.TypeVectorAnyGeometry,
                None,
                True,
            )
        )

        # RECTANGLE DETECTION - LEVEL 3
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RECTANGLE_LEVEL_3,
                self.tr("Detection of rectangular shapes - Level 3"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SD_CONVEX_RECT_3,
                self.tr("Surface distance with convex hull (level 3)"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                maxValue=1.0,
                defaultValue=0.15,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SD_MBR_RECT_3,
                self.tr("Surface distance with MBR (level 3)"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                maxValue=1.0,
                defaultValue=0.15,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.RECT_3_LAYER_OUTPUT,
                self.tr("Rectangles - level 3"),
                QgsProcessing.TypeVectorAnyGeometry,
                None,
                True,
            )
        )

        # RECTANGULAR_GROUP = 'RECTANGULAR_GROUP'
        # RECTANGULAR_GROUP_LAYER_INPUT = 'RECTANGULAR_GROUP_LAYER_INPUT'
        # SD_CONVEX_RECT_GROUP = 'SD_CONVEX_RECT_GROUP'
        # SD_MBR_RECT_GROUP = 'SD_MBR_RECT_GROUP'
        # RECT_GROUP_LAYER_OUTPUT = 'RECT_GROUP_LAYER_OUTPUT'

        # CIRCULAR_SHAPE = 'CIRCULAR_SHAPE'
        # MILLER_INDEX = 'MILLER_INDEX'
        # CIRCULAR_LAYER_OUTPUT = 'CIRCULAR_LAYER_OUTPUT'

        # CIRCLE
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MILLER_INDEX,
                self.tr("Circularity threshold"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                maxValue=1.0,
                defaultValue=0.9,
            )
        )

    def name(self):
        return "rectangular_characterisation"

    def displayName(self):
        # TODO IMPROVE
        return self.tr("Rectangular characterisation")

    def processAlgorithm(self, parameters, context, feedback):
        # ignore_ring_self_intersection = self.parameterAsBoolean(parameters, self.IGNORE_RING_SELF_INTERSECTION, context)
        # method_param = self.parameterAsEnum(parameters, self.METHOD, context)
        # if method_param == 0:
        #     settings = QgsSettings()
        #     method = int(settings.value(settings_method_key, 0)) - 1
        #     if method < 0:
        #         method = 0
        # else:
        #     method = method_param - 1

        # TODO ADD PROPER METHOD
        results = self.process(0, parameters, context, feedback)
        return results

    def process(self, method, parameters, context, feedback):
        # flags = QgsGeometry.FlagAllowSelfTouchingHoles if ignore_ring_self_intersection else QgsGeometry.ValidityFlags()

        source_layer = self.parameterAsLayer(parameters, self.INPUT_LAYER, context)

        rect_level_1 = self.parameterAsBoolean(
            parameters, self.RECTANGLE_LEVEL_1, context
        )
        sd_convex_level_1 = self.parameterAsDouble(
            parameters, self.SD_CONVEX_RECT_1, context
        )
        sd_mbr_level_1 = self.parameterAsDouble(parameters, self.SD_MBR_RECT_1, context)

        rect_level_2 = self.parameterAsBoolean(
            parameters, self.RECTANGLE_LEVEL_2, context
        )
        sd_convex_level_2 = self.parameterAsDouble(
            parameters, self.SD_CONVEX_RECT_2, context
        )
        sd_mbr_level_2 = self.parameterAsDouble(parameters, self.SD_MBR_RECT_2, context)

        rect_level_3 = self.parameterAsBoolean(
            parameters, self.RECTANGLE_LEVEL_3, context
        )
        sd_convex_level_3 = self.parameterAsDouble(
            parameters, self.SD_CONVEX_RECT_3, context
        )
        sd_mbr_level_3 = self.parameterAsDouble(parameters, self.SD_MBR_RECT_3, context)

        miller_index_threshold = self.parameterAsDouble(
            parameters, self.MILLER_INDEX, context
        )

        source = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT_LAYER)
            )

        fields = source.fields()
        new_fields = QgsFields()
        new_fields.append(QgsField("SD_CONVEX", QVariant.Double))
        new_fields.append(QgsField("SD_MBR", QVariant.Double))

        new_fields.append(QgsField("ORIENT_REC", QVariant.Double))
        new_fields.append(QgsField("MILLER_IND", QVariant.Double))
        new_fields.append(QgsField("CIRCLE", QVariant.Bool))
        new_fields.append(QgsField("ELONGATION", QVariant.Double))

        fields = QgsProcessingUtils.combineFields(fields, new_fields)

        (rect_1_output_sink, rect_1_output_dest_id) = self.parameterAsSink(
            parameters,
            self.RECT_1_LAYER_OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs(),
        )

        rect_1_count = 0
        if rect_1_output_sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.RECT_1_LAYER_OUTPUT)
            )

        (rect_2_output_sink, rect_2_output_dest_id) = self.parameterAsSink(
            parameters,
            self.RECT_2_LAYER_OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs(),
        )

        rect_2_count = 0
        if rect_2_output_sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.RECT_2_LAYER_OUTPUT)
            )

        (rect_3_output_sink, rect_3_output_dest_id) = self.parameterAsSink(
            parameters,
            self.RECT_3_LAYER_OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs(),
        )

        rect_3_count = 0
        if rect_3_output_sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.RECT_3_LAYER_OUTPUT)
            )

        distance_area = QgsDistanceArea()

        features = source.getFeatures(
            QgsFeatureRequest(),
            QgsProcessingFeatureSource.FlagSkipGeometryValidityChecks,
        )
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, f in enumerate(features):
            if feedback.isCanceled():
                break

            geom = f.geometry()
            attrs = f.attributes()
            sd_convex_hull = -2.0
            sd_mbr = -2.0
            mbr_orientation = -1.0

            if not geom.isNull() and not geom.isEmpty():
                sd_convex_hull, sd_mbr, mbr_orientation = geometry_utils.is_rectangle_indices(
                    geom, distance_area
                )
                # index_rect = is_rectangle_indices(
                #     geom,
                #     sd_convex_level_1,
                #     sd_mbr_level_1,
                #     distance_area
                # )
                index_compact = geometry_utils.compactedness_miller_index(geom, distance_area)
                index_circle = geometry_utils.is_circle(geom, miller_index_threshold, distance_area)
                elongation = geometry_utils.polygon_elongation(geom)
                attrs.extend(
                    [
                        sd_convex_hull,
                        sd_mbr,
                        mbr_orientation,
                        index_compact,
                        index_circle,
                        elongation
                    ]
                )

            if len(attrs) < len(fields):
                attrs += [NULL] * (len(fields) - len(attrs))

            if mbr_orientation != -1.0:
                outFeat = QgsFeature()
                outFeat.setGeometry(geom)
                outFeat.setAttributes(attrs)

                if sd_convex_hull != -2.0:
                    if rect_level_1:
                        if (
                            sd_convex_hull <= sd_convex_level_1
                            and sd_mbr <= sd_mbr_level_1
                        ):
                            rect_1_output_sink.addFeature(
                                outFeat, QgsFeatureSink.FastInsert
                            )
                            rect_1_count += 1
                        else:
                            if rect_level_2:
                                if (
                                    sd_convex_hull <= sd_convex_level_2
                                    and sd_mbr <= sd_mbr_level_2
                                ):
                                    rect_2_output_sink.addFeature(
                                        outFeat, QgsFeatureSink.FastInsert
                                    )
                                    rect_2_count += 1
                                else:
                                    if rect_level_3:
                                        if (
                                            sd_convex_hull <= sd_convex_level_3
                                            and sd_mbr <= sd_mbr_level_3
                                        ):
                                            rect_3_output_sink.addFeature(
                                                outFeat, QgsFeatureSink.FastInsert
                                            )
                                            rect_3_count += 1

            feedback.setProgress(int(current * total))

        results = {
            self.RECT_1_COUNT: rect_1_count,
            self.RECT_2_COUNT: rect_2_count,
            self.RECT_3_COUNT: rect_3_count,
        }

        global rect_1_renamer, rect_2_renamer, rect_3_renamer

        rect_1_newname = '{}-Rectangles-Level_1-{}-{}'.format(
            source_layer.name(),
            sd_convex_level_1,
            sd_mbr_level_1
        )
        rect_1_renamer = LayerRenamer(rect_1_newname)
        context.layerToLoadOnCompletionDetails(
            rect_1_output_dest_id).setPostProcessor(rect_1_renamer)

        rect_2_newname = '{}-Rectangles-Level_2-{}-{}'.format(
            source_layer.name(),
            sd_convex_level_2,
            sd_mbr_level_2
        )
        rect_2_renamer = LayerRenamer(rect_2_newname)
        context.layerToLoadOnCompletionDetails(
            rect_2_output_dest_id).setPostProcessor(rect_2_renamer)

        rect_3_newname = '{}-Rectangles-Level_3-{}-{}'.format(
            source_layer.name(),
            sd_convex_level_3,
            sd_mbr_level_3
        )
        rect_3_renamer = LayerRenamer(rect_3_newname)
        context.layerToLoadOnCompletionDetails(
            rect_3_output_dest_id).setPostProcessor(rect_3_renamer)

        if rect_1_output_sink:
            results[self.RECT_1_LAYER_OUTPUT] = rect_1_output_dest_id
        if rect_1_output_sink:
            results[self.RECT_2_LAYER_OUTPUT] = rect_2_output_dest_id
        if rect_1_output_sink:
            results[self.RECT_3_LAYER_OUTPUT] = rect_3_output_dest_id

        return results
