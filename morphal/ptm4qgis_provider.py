# -*- coding: utf-8 -*-

"""
/***************************************************************************
    ptm4qgis_provider.py
    Part of the Paris Time Machine plugin for QGIS
    --------------
    Date                 : January 2021
    Copyright            : (C) 2021, Eric Grosso, Paris Time Machine
    Email                : eric dot ptm at thefactory dot io
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

__author__ = 'Eric Grosso'
__date__ = 'January 2021'
__copyright__ = '(C) 2021, Eric Grosso, Paris Time Machine'

from qgis.core import QgsProcessingProvider

from .morphal.morphal_polygon_perimeter_area import MorphALPolygonPerimeterArea
from .morphal.morphal_geometry_to_segments import MorphALGeometryToSegments
from .morphal.morphal_segment_orientation import MorphALSegmentOrientation
from .morphal.morphal_rectangular_characterisation import MorphALRectangularCharacterisation

class PTM4QgisProvider(QgsProcessingProvider):

    def __init__(self):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        self.addAlgorithm(MorphALPolygonPerimeterArea())
        self.addAlgorithm(MorphALGeometryToSegments())
        self.addAlgorithm(MorphALSegmentOrientation())
        self.addAlgorithm(MorphALRectangularCharacterisation())

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'paristimemachine'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('Paris Time Machine')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()
