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

import itertools
import math

from qgis.core import (
    NULL,
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsPoint,
    QgsPolygon,
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingUtils,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

from morphal.ptm4qgis_algorithm import PTM4QgisAlgorithm

from . import morphal_geometry_utils as geometry_utils
from .utils import LayerRenamer, round_float_to_3_decimals


class MorphALPolygonIndicators(PTM4QgisAlgorithm):

    INPUT_LAYER = "INPUT_LAYER"
    METHOD = "CALC_METHOD"

    PERIMETER = "PERIMETER"
    AREA = "AREA"

    SCHUM_ELONGATION = "SCHUM_ELONGATION"
    MORTON_INDEX = "MORTON_INDEX"
    ALTERNATIVE_COMPACITY = "ALTERNATIVE_COMPACITY"
    ALTERNATIVE_CIRCLE_COMPACITY = "ALTERNATIVE_CIRCLE_COMPACITY"
    GRAVELIUS_INDEX = "GRAVELIUS_INDEX"
    MILLER_INDEX = "MILLER_INDEX"
    ELONGATION = "ELONGATION"
    AREA_CONV_DEFECT = "AREA_CONV_DEFECT"
    PERIMETER_CONV_DEFECT = "PERIMETER_CONV_DEFECT"
    RECTANGULAR_DIFFERENCE = "RECTANGULAR_DIFFERENCE"
    OUTPUT_LAYER = "OUTPUT_LAYER"

    def help(self):
        # TODO improve help text
        return self.tr("Compute morphological indicators for polygons")

    def __init__(self):
        super().__init__()
        self.distance_area = None
        self.calc_methods = [
            self.tr("Layer CRS"),
            self.tr("Project CRS"),
            self.tr("Ellipsoidal"),
        ]

    def initAlgorithm(self, config):
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

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.PERIMETER,
                self.tr("Perimeter"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.AREA,
                self.tr("Area"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SCHUM_ELONGATION,
                self.tr("Schum elongation"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MORTON_INDEX,
                self.tr("Morton index (spreading)"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ALTERNATIVE_COMPACITY,
                self.tr("Alternative compacity"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ALTERNATIVE_CIRCLE_COMPACITY,
                self.tr("Alternative circle compacity"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.GRAVELIUS_INDEX,
                self.tr("Gravelius' compactness index"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MILLER_INDEX,
                self.tr("Miller's compactness index (roundness)"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ELONGATION,
                self.tr("Polygonal elongation (based on MBR)"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.AREA_CONV_DEFECT,
                self.tr("Area convexity defect"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.PERIMETER_CONV_DEFECT,
                self.tr("Perimeter convexity defect"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RECTANGULAR_DIFFERENCE,
                self.tr("Rectangular difference"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LAYER, self.tr("Morphological indicators")
            )
        )

    def name(self):
        return "polygon_morphological_indicators"

    def displayName(self):
        return self.tr("Compute morphological indicators for polygons")

    def processAlgorithm(self, parameters, context, feedback):
        # input / source
        source = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT_LAYER)
            )

        wkb_type = source.wkbType()

        if QgsWkbTypes.geometryType(wkb_type) != QgsWkbTypes.PolygonGeometry:
            feedback.reportError("The layer geometry type is different from a polygon")
            return {}

        if source.featureCount() == 0:
            feedback.reportError(
                self.tr("The layer doesn't contain any feature: no output provided")
            )
            return {}

        # other parameters

        # Calculate with projection:
        # 0 - layer CRS
        # 1 - project CRS
        # 2 - ellipsoidal
        method = self.parameterAsEnum(parameters, self.METHOD, context)
        method = self.parameterAsEnum(parameters, self.METHOD, context)

        perimeter_compute = self.parameterAsBoolean(
            parameters, self.PERIMETER, context
        )

        area_compute = self.parameterAsBoolean(
            parameters, self.AREA, context
        )

        schum_compute = self.parameterAsBoolean(
            parameters, self.SCHUM_ELONGATION, context
        )

        morton_compute = self.parameterAsBoolean(
            parameters, self.MORTON_INDEX, context
        )

        alt_compacity_compute = self.parameterAsBoolean(
            parameters, self.ALTERNATIVE_COMPACITY, context
        )

        alt_circle_compacity_compute = self.parameterAsBoolean(
            parameters, self.ALTERNATIVE_CIRCLE_COMPACITY, context
        )

        gravelius_compute = self.parameterAsBoolean(
            parameters, self.GRAVELIUS_INDEX, context
        )

        miller_compute = self.parameterAsBoolean(
            parameters, self.MILLER_INDEX, context
        )

        elongation_compute = self.parameterAsBoolean(
            parameters, self.ELONGATION, context
        )

        area_conv_defect_compute = self.parameterAsBoolean(
            parameters, self.AREA_CONV_DEFECT, context
        )

        perimeter_conv_defect_compute = self.parameterAsBoolean(
            parameters, self.PERIMETER_CONV_DEFECT, context
        )

        rectangular_diff_compute = self.parameterAsBoolean(
            parameters, self.RECTANGULAR_DIFFERENCE, context
        )

        # output
        fields = source.fields()

        new_fields = QgsFields()

        if perimeter_compute:
            new_fields.append(QgsField("PERIMETER", QVariant.Double))

        if area_compute:
            new_fields.append(QgsField("AREA", QVariant.Double))

        if schum_compute:
            new_fields.append(QgsField("SCHUM", QVariant.Double))

        if morton_compute:
            new_fields.append(QgsField("MORTON", QVariant.Double))

        if alt_compacity_compute:
            new_fields.append(QgsField("ALT_COMP", QVariant.Double))

        if alt_circle_compacity_compute:
            new_fields.append(QgsField("ALT_C_COMP", QVariant.Double))

        if gravelius_compute:
            new_fields.append(QgsField("GRAVELIUS", QVariant.Double))

        if miller_compute:
            new_fields.append(QgsField("MILLER", QVariant.Double))

        if elongation_compute:
            new_fields.append(QgsField("ELONGATION", QVariant.Double))

        if area_conv_defect_compute:
            new_fields.append(QgsField("A_CONV_DEF", QVariant.Double))

        if perimeter_conv_defect_compute:
            new_fields.append(QgsField("P_CONV_DEF", QVariant.Double))

        if rectangular_diff_compute:
            new_fields.append(QgsField("RECT_DIFF", QVariant.Double))

        fields = QgsProcessingUtils.combineFields(fields, new_fields)
        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT_LAYER, context, fields, wkb_type, source.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT_LAYER))

        coord_transform = None

        self.distance_area = QgsDistanceArea()
        if method == 2:
            self.distance_area.setSourceCrs(
                source.sourceCrs(), context.transformContext()
            )
            self.distance_area.setEllipsoid(context.ellipsoid())
        elif method == 1:
            if not context.project():
                raise QgsProcessingException(
                    self.tr("No project is available in this context")
                )
            coord_transform = QgsCoordinateTransform(
                source.sourceCrs(), context.project().crs(), context.project()
            )

        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, f in enumerate(features):
            if feedback.isCanceled():
                return {}

            out_feat = f
            attrs = f.attributes()
            in_geom = f.geometry()
            if in_geom:
                if coord_transform is not None:
                    in_geom.transform(coord_transform)

                attrs.extend(self.polygon_indicators(
                    in_geom,
                    perimeter_compute,
                    area_compute,
                    schum_compute,
                    morton_compute,
                    alt_compacity_compute,
                    alt_circle_compacity_compute,
                    gravelius_compute,
                    miller_compute,
                    elongation_compute,
                    area_conv_defect_compute,
                    perimeter_conv_defect_compute,
                    rectangular_diff_compute)
                )

            # ensure consistent count of attributes - otherwise null
            # geometry features will have incorrect attribute length
            # and provider may reject them
            if len(attrs) < len(fields):
                attrs += [NULL] * (len(fields) - len(attrs))

            out_feat.setAttributes(attrs)
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        # rename output layer
        global morph_indicators_renamer

        morph_indicators_newname = f'{source.sourceName()}-'
        morph_indicators_newname += self.tr("Morphological_indicators")

        morph_indicators_renamer = LayerRenamer(morph_indicators_newname)
        context.layerToLoadOnCompletionDetails(
            dest_id).setPostProcessor(morph_indicators_renamer)

        return {self.OUTPUT_LAYER: dest_id}

    def polygon_indicators(
            self,
            polygon: QgsPolygon,
            c_perimeter: bool,
            c_area: bool,
            c_elongation_schum: bool,
            c_morton_index: bool,
            c_comp_alt: bool,
            c_comp_circle_alt: bool,
            c_gravelius: bool,
            c_miller: bool,
            c_elongation: bool,
            c_area_conv_defect: bool,
            c_perimeter_conv_defect: bool,
            c_rectangular_diff: bool
    ):
        indicators = []
        perimeter = self.distance_area.measurePerimeter(polygon)
        area = self.distance_area.measureArea(polygon)

        # TODO IMPROVE
        if area <= 0.000000001:
            return indicators

        convex_hull = polygon.convexHull()
        convex_hull_perimeter = self.distance_area.measurePerimeter(convex_hull)
        convex_hull_area = self.distance_area.measureArea(convex_hull)

        (mbr, mbr_area, mbr_angle, mbr_width, mbr_height) = polygon.orientedMinimumBoundingBox()
        # mbr_perimeter = self.distance_area.measurePerimeter(mbr)
        mbr_area = self.distance_area.measureArea(mbr)
        if mbr_width >= mbr_height:
            mbr_elongation = mbr_width / mbr_height
        else:
            mbr_elongation = mbr_height / mbr_width

        # max axis
        vertices = [v for v in polygon.vertices()]
        dist_max = max([distance_vertices(v1, v2, self.distance_area) for v1, v2 in itertools.combinations(vertices, 2)])

        if c_perimeter:
            perimeter_r = round_float_to_3_decimals(perimeter)
            indicators.append(perimeter_r)

        if c_area:
            area_r = round_float_to_3_decimals(area)
            indicators.append(area_r)

        if c_elongation_schum:
            elongation_schum = math.sqrt(area) / (dist_max * math.sqrt(math.pi))
            elongation_schum = round_float_to_3_decimals(elongation_schum)
            indicators.append(elongation_schum)

        if c_morton_index:
            morton_index = 4 * area / (dist_max * dist_max * math.pi)
            morton_index = round_float_to_3_decimals(morton_index)
            indicators.append(morton_index)

        if c_comp_alt:
            comp_alt = perimeter * perimeter / area
            comp_alt = round_float_to_3_decimals(comp_alt)
            indicators.append(comp_alt)

        if c_comp_circle_alt:
            comp_circle_alt = area / (math.pi * math.pow(0.5 * dist_max, 2))
            comp_circle_alt = round_float_to_3_decimals(comp_circle_alt)
            indicators.append(comp_circle_alt)

        if c_gravelius:
            gravelius_index = geometry_utils.compactness_gravelius_index_from_precomputed_parameters(
                perimeter,
                area
            )
            gravelius_index = round_float_to_3_decimals(gravelius_index)
            indicators.append(gravelius_index)

        if c_miller:
            miller_index = geometry_utils.compactness_miller_index_from_precomputed_parameters(
                perimeter,
                area)
            miller_index = round_float_to_3_decimals(miller_index)
            indicators.append(miller_index)

        if c_elongation:
            elongation = round_float_to_3_decimals(mbr_elongation)
            indicators.append(elongation)

        if c_area_conv_defect:
            conv_defect_area = area / convex_hull_area
            conv_defect_area = round_float_to_3_decimals(conv_defect_area)
            indicators.append(conv_defect_area)

        if c_perimeter_conv_defect:
            conv_defect_perimeter = convex_hull_perimeter / perimeter
            conv_defect_perimeter = round_float_to_3_decimals(conv_defect_perimeter)
            indicators.append(conv_defect_perimeter)

        if c_rectangular_diff:
            rect_diff = area / mbr_area
            rect_diff = round_float_to_3_decimals(rect_diff)
            indicators.append(rect_diff)

        return indicators


def distance_vertices(vertice_1: QgsPoint, vertice_2: QgsPoint, distance_area: QgsDistanceArea):
    seg = geometry_utils.create_normalized_segment(vertice_1, vertice_2)
    return distance_area.measureLength(seg)
