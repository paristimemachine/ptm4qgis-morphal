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
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingException,
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


class MorphALGeometryToMedians(PTM4QgisAlgorithm):
    INPUT_LAYER = "INPUT_LAYER"
    METHOD = "CALC_METHOD"
    ORIENTATION_ORIGIN = "ORIENTATION_ORIGIN"
    OUTPUT_LAYER = "OUTPUT_LAYER"

    def help(self):
        return self.tr("\
            This algorithm generates a segment layer representing the medians of the geometries\
            from an input line layer or an input polygon layer.\
            \nThese segments are normalised, i.e. their point of origin is always located as far west \
            as possible, or otherwise as far south as possible.\
            \nIt creates a new vector layer with the same content as the input one, but with\
            additional computed attributes: median orientation, computed from East or from North,\
            median length and median associated elongation.")

    def __init__(self):
        super().__init__()
        self.distance_area = None
        self.calc_methods = [self.tr("Layer CRS"),
                             self.tr("Project CRS"),
                             self.tr("Ellipsoidal")]
        self.orientation_origins = [
            self.tr("East"),
            self.tr("North")
        ]

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                self.tr("Input layer"),
                types=[QgsProcessing.TypeVectorLine, QgsProcessing.TypeVectorPolygon],
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
            QgsProcessingParameterEnum(
                self.ORIENTATION_ORIGIN,
                self.tr("Orientations calculated from"),
                options=self.orientation_origins,
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LAYER,
                self.tr("Medians"),
                type=QgsProcessing.TypeVectorLine
            )
        )

    def name(self):
        return "geometry_to_medians"

    def displayName(self):
        return self.tr("Geometries to medians")

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

        # other parameters

        # Calculate with projection:
        # 0 - layer CRS
        # 1 - project CRS
        # 2 - ellipsoidal
        method = self.parameterAsEnum(parameters, self.METHOD, context)

        # Orientation origin:
        # 0 - East
        # 1 - North
        orientation_origin = self.parameterAsEnum(parameters, self.ORIENTATION_ORIGIN, context)
        from_north = False
        if orientation_origin == 1:
            from_north = True

        # output
        fields = source.fields()

        new_fields = QgsFields()
        if from_north:
            new_fields.append(QgsField("N_ORIENTATION", QVariant.Double))
        else:
            new_fields.append(QgsField("E_ORIENTATION", QVariant.Double))

        new_fields.append(QgsField("LENGTH", QVariant.Double))
        new_fields.append(QgsField("ELONGATION", QVariant.Double))

        fields = QgsProcessingUtils.combineFields(fields, new_fields)

        if method == 1:
            (sink, dest_id) = self.parameterAsSink(
                parameters,
                self.OUTPUT_LAYER,
                context,
                fields,
                QgsWkbTypes.LineString,
                context.project().crs(),
            )
        else:
            (sink, dest_id) = self.parameterAsSink(
                parameters,
                self.OUTPUT_LAYER,
                context,
                fields,
                QgsWkbTypes.LineString,
                source.sourceCrs(),
            )
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT_LAYER))

        # process
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

            out_feature = f
            attrs = f.attributes()
            geom = f.geometry()

            if not f.hasGeometry():
                continue

            # else
            if coord_transform is not None:
                geom.transform(coord_transform)

            median_geom, median_orientation, median_length, mbr_elongation = geometry_utils.median_segment(
                geom,
                from_north,
                self.distance_area
            )
            attrs.extend([median_orientation, median_length, mbr_elongation])
            out_feature.setGeometry(median_geom)

            # ensure consistent count of attributes - otherwise null
            # geometry features will have incorrect attribute length
            # and provider may reject them
            if len(attrs) < len(fields):
                attrs += [NULL] * (len(fields) - len(attrs))

            out_feature.setAttributes(attrs)
            sink.addFeature(out_feature, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        # rename output layer
        global medians_renamer

        medians_newname = f'{source.sourceName()}-{self.tr("Medians")}-'

        if from_north:
            medians_newname += self.tr("North")
        else:
            medians_newname += self.tr("East")

        medians_renamer = LayerRenamer(medians_newname)
        context.layerToLoadOnCompletionDetails(
            dest_id).setPostProcessor(medians_renamer)

        return {self.OUTPUT_LAYER: dest_id}
