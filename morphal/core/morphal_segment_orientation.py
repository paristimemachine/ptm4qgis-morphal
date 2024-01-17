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

from ..ptm4qgis_algorithm import PTM4QgisAlgorithm

# from qgis import processing
from .morphal_geometry_utils import *


class MorphALSegmentOrientation(PTM4QgisAlgorithm):
    INPUT = "INPUT"
    UNIT = "UNIT"
    INTERVAL = "INTERVAL"
    METHOD = "CALC_METHOD"
    ROUNDED = "ROUNDED"
    HISTOGRAM = "HISTOGRAM"
    HISTOGRAM_STEP = "HISTOGRAM_STEP"
    CLASSIFICATION = "CLASSIFICATION"
    CLASSIFICATION_STEP = "CLASSIFICATION_STEP"
    OUTPUT = "OUTPUT"

    def help(self):
        # TODO improve help text
        return self.tr("Compute the orientations of a layer of segments")

    def group(self):
        return self.tr("MorphAL")

    def groupId(self):
        return "morphal"

    def __init__(self):
        super().__init__()
        self.export_z = False
        self.export_m = False
        self.distance_area = None
        self.units = [self.tr("Degree"), self.tr("Radian"), self.tr("Grade")]
        self.intervals = [self.tr("[0 ; Pi["), self.tr("[0 ; Pi/2[")]
        # self.calc_methods = [self.tr('Layer CRS'),
        #                      self.tr('Project CRS'),
        #                      self.tr('Ellipsoidal')]
        self.calc_methods = [self.tr("Layer CRS"), self.tr("Project CRS")]
        self.errors = ""

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT, self.tr("Input layer"), types=[QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.UNIT, self.tr("Unit"), options=self.units, defaultValue=0
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
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr("Calculate using"),
                options=self.calc_methods,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ROUNDED,
                self.tr("Rounded orientation result (3 digits)"),
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

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.HISTOGRAM, self.tr("Create an histogram"), defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.HISTOGRAM_STEP,
                self.tr("Step of the histogram"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.001,
                maxValue=200,
                defaultValue=5,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT, self.tr("Segments with orientation")
            )
        )

    def name(self):
        return "morphalsegmentorientation"

    def displayName(self):
        # TODO IMPROVE TEXT
        return self.tr("Compute the orientations of a layer of segments")

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        # Unit:
        # 0 - degree
        # 1 - radian
        # 2 - grade
        unit = self.parameterAsEnum(parameters, self.UNIT, context)
        # Interval:
        # 0 - [0 ; Pi[
        # 1 - [0 ; Pi/2[
        interval = self.parameterAsEnum(parameters, self.INTERVAL, context)
        # Calculate with projection:
        # 0 - layer CRS
        # 1 - project CRS
        # 2 - ellipsoidal (TODO: NOT USED AT THE MOMENT)
        method = self.parameterAsEnum(parameters, self.METHOD, context)

        rounded = self.parameterAsBoolean(parameters, self.ROUNDED, context)

        classification = self.parameterAsBoolean(
            parameters, self.CLASSIFICATION, context
        )
        classification_step = self.parameterAsDouble(
            parameters, self.CLASSIFICATION_STEP, context
        )

        histogram = self.parameterAsBoolean(parameters, self.HISTOGRAM, context)
        histogram_step = self.parameterAsDouble(
            parameters, self.HISTOGRAM_STEP, context
        )

        wkb_type = source.wkbType()

        # TODO ? improvement: test if the layer contains at least one segment
        if QgsWkbTypes.geometryType(wkb_type) != QgsWkbTypes.LineGeometry:
            # TODO IMPROVE FEEDBACK
            feedback.reportError("The layer geometry type is different from a line")
            return {}

        fields = source.fields()

        new_fields = QgsFields()
        new_fields.append(QgsField("orientation", QVariant.Double))
        if classification:
            new_fields.append(QgsField("classification", QVariant.Double))

        fields = QgsProcessingUtils.combineFields(fields, new_fields)
        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields, wkb_type, source.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        coord_transform = None

        self.distance_area = QgsDistanceArea()
        # if method == 2:
        #     self.distance_area.setSourceCrs(source.sourceCrs(), context.transformContext())
        #     self.distance_area.setEllipsoid(context.ellipsoid())
        if method == 1:
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
                break

            out_feature = f
            attrs = f.attributes()
            geom = f.geometry()
            if geom:
                if coord_transform is not None:
                    geom.transform(coord_transform)

                orientation = angle(geom, unit, interval, rounded)
                if orientation is not None:
                    if classification:
                        class_int = int(orientation / classification_step)
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

        return {self.OUTPUT: dest_id}
