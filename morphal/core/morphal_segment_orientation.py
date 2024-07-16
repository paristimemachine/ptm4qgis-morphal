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
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingUtils,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

from morphal.ptm4qgis_algorithm import PTM4QgisAlgorithm

from . import morphal_geometry_utils as geometry_utils
from .utils import LayerRenamer, round_float_to_3_decimals


class MorphALSegmentOrientation(PTM4QgisAlgorithm):
    INPUT = "INPUT"
    METHOD = "CALC_METHOD"
    ORIENTATION_ORIGIN = "ORIENTATION_ORIGIN"
    UNIT = "UNIT"
    INTERVAL = "INTERVAL"
    ROUNDED = "ROUNDED"
    # HISTOGRAM = "HISTOGRAM"
    # HISTOGRAM_STEP = "HISTOGRAM_STEP"
    CLASSIFICATION = "CLASSIFICATION"
    CLASSIFICATION_STEP = "CLASSIFICATION_STEP"
    OUTPUT = "OUTPUT"

    def help(self):
        return self.tr("Compute the orientations of a layer of segments")

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
        self.units = [
            self.tr("Degree"),
            self.tr("Radian"),
            self.tr("Grade")
        ]
        self.intervals = [
            self.tr("[0 ; Pi["),
            self.tr("[0 ; Pi/2[")
        ]
        self.errors = ""

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr("Input layer"),
                types=[QgsProcessing.TypeVectorLine]
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
            QgsProcessingParameterEnum(
                self.UNIT,
                self.tr("Unit"),
                options=self.units,
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.INTERVAL,
                self.tr("Interval"),
                options=self.intervals,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ROUNDED,
                self.tr("Round orientations to 3 decimals"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CLASSIFICATION,
                self.tr("Compute a classification"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.CLASSIFICATION_STEP,
                self.tr("Step of the classification"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.001,
                maxValue=200,
                defaultValue=10,
            )
        )

        # self.addParameter(
        #     QgsProcessingParameterBoolean(
        #         self.HISTOGRAM, self.tr("Create an histogram"), defaultValue=False
        #     )
        # )

        # self.addParameter(
        #     QgsProcessingParameterNumber(
        #         self.HISTOGRAM_STEP,
        #         self.tr("Step of the histogram"),
        #         type=QgsProcessingParameterNumber.Double,
        #         minValue=0.001,
        #         maxValue=200,
        #         defaultValue=5,
        #     )
        # )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Segments with orientations"),
                type=QgsProcessing.TypeVectorLine
            )
        )

    def name(self):
        return "segment_orientation"

    def displayName(self):
        return self.tr("Compute segments orientations")

    def processAlgorithm(self, parameters, context, feedback):
        # input / source
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        wkb_type = source.wkbType()

        if QgsWkbTypes.geometryType(wkb_type) != QgsWkbTypes.LineGeometry:
            feedback.reportError("The layer geometry type is different from a line")
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

        # Unit:
        # 0 - degree
        # 1 - radian
        # 2 - grade
        unit = self.parameterAsEnum(parameters, self.UNIT, context)

        # Interval:
        # 0 - [0 ; Pi[
        # 1 - [0 ; Pi/2[
        interval = self.parameterAsEnum(parameters, self.INTERVAL, context)

        rounded = self.parameterAsBoolean(parameters, self.ROUNDED, context)

        classification = self.parameterAsBoolean(
            parameters, self.CLASSIFICATION, context
        )
        classification_step = self.parameterAsDouble(
            parameters, self.CLASSIFICATION_STEP, context
        )

        # histogram = self.parameterAsBoolean(parameters, self.HISTOGRAM, context)
        # histogram_step = self.parameterAsDouble(
        #     parameters, self.HISTOGRAM_STEP, context
        # )

        # output
        fields = source.fields()

        new_fields = QgsFields()
        if from_north:
            new_fields.append(QgsField("N_ORIENTATION", QVariant.Double))
        else:
            new_fields.append(QgsField("E_ORIENTATION", QVariant.Double))

        if classification:
            if from_north:
                new_fields.append(QgsField("N_CLASSIFICATION", QVariant.Double))
            else:
                new_fields.append(QgsField("E_CLASSIFICATION", QVariant.Double))

        fields = QgsProcessingUtils.combineFields(fields, new_fields)

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields, wkb_type, source.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT)
            )

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
            if geom:
                if coord_transform is not None:
                    geom.transform(coord_transform)

                orientation = geometry_utils.angle_north_east(
                    geom,
                    unit,
                    interval,
                    rounded,
                    from_north
                    )

                if orientation is not None:
                    if classification:
                        class_int = int(orientation / classification_step)
                        if orientation < 0:
                            class_int = class_int - 1
                        attrs.extend([orientation, class_int])
                    else:
                        attrs.extend([orientation])

            # ensure consistent count of attributes - otherwise null
            # geometry features will have incorrect attribute length
            # and provider may reject them
            if len(attrs) < len(fields):
                attrs += [NULL] * (len(fields) - len(attrs))

            out_feature.setAttributes(attrs)
            sink.addFeature(out_feature, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        # rename output layer
        global orientations_renamer

        orientations_newname = f'{source.sourceName()}-Orientations-'

        if from_north:
            orientations_newname += self.tr("North")
        else:
            orientations_newname += self.tr("East")

        if classification:
            orientations_newname += f'-{round_float_to_3_decimals(classification_step)}'

        orientations_renamer = LayerRenamer(orientations_newname)
        context.layerToLoadOnCompletionDetails(
            dest_id).setPostProcessor(orientations_renamer)

        return {self.OUTPUT: dest_id}
