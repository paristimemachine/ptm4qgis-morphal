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

from ..ptm4qgis_algorithm import PTM4QgisAlgorithm


class MorphALPolygonPerimeterArea(PTM4QgisAlgorithm):
    INPUT = "INPUT"
    METHOD = "CALC_METHOD"
    OUTPUT = "OUTPUT"

    def help(self):
        # TODO improve help text
        return self.tr("Compute the perimeters and areas of a layer of polygons")

    def __init__(self):
        super().__init__()
        self.export_z = False
        self.export_m = False
        self.distance_area = None
        self.calc_methods = [
            self.tr("Layer CRS"),
            self.tr("Project CRS"),
            self.tr("Ellipsoidal"),
        ]

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
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
            QgsProcessingParameterFeatureSink(
                self.OUTPUT, self.tr("Layer with added perimeters and areas")
            )
        )

    def name(self):
        return "morphalpolygonperimeterarea"

    def displayName(self):
        # TODO IMPROVE TEXT
        return self.tr("Compute the perimeters and areas of a layer of polygons")

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        method = self.parameterAsEnum(parameters, self.METHOD, context)

        wkb_type = source.wkbType()

        if QgsWkbTypes.geometryType(wkb_type) != QgsWkbTypes.PolygonGeometry:
            # TODO IMPROVE FEEDBACK
            feedback.reportError("The layer geometry type is different from a polygon")
            return {}

        fields = source.fields()

        new_fields = QgsFields()
        new_fields.append(QgsField("perimeter", QVariant.Double))
        new_fields.append(QgsField("area", QVariant.Double))

        fields = QgsProcessingUtils.combineFields(fields, new_fields)
        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields, wkb_type, source.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        coordTransform = None

        # Calculate with:
        # 0 - layer CRS
        # 1 - project CRS
        # 2 - ellipsoidal

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
            coordTransform = QgsCoordinateTransform(
                source.sourceCrs(), context.project().crs(), context.project()
            )

        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, f in enumerate(features):
            if feedback.isCanceled():
                break

            outFeat = f
            attrs = f.attributes()
            inGeom = f.geometry()
            if inGeom:
                if coordTransform is not None:
                    inGeom.transform(coordTransform)

                attrs.extend(self.polygon_attributes(inGeom))

            # ensure consistent count of attributes - otherwise null
            # geometry features will have incorrect attribute length
            # and provider may reject them
            if len(attrs) < len(fields):
                attrs += [NULL] * (len(fields) - len(attrs))

            outFeat.setAttributes(attrs)
            sink.addFeature(outFeat, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def polygon_attributes(self, geometry):
        perimeter = self.distance_area.measurePerimeter(geometry)
        area = self.distance_area.measureArea(geometry)
        return [perimeter, area]
