# -*- coding: utf-8 -*-

"""
/***************************************************************************
    morphal_geometry_utils.py
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

from qgis.core import QgsProcessingAlgorithm, QgsProcessingFeatureBasedAlgorithm
from qgis.PyQt.QtCore import QCoreApplication
# from processing.algs.help import shortHelp

class PTM4QgisAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()

    def shortHelpString(self):
        # TODO TO IMPROVE
        # return shortHelp.get(self.id(), None)
        return self.help()

    def tr(self, string, context=''):
        if context == '':
            context = self.__class__.__name__
        return QCoreApplication.translate(context, string)

    def trAlgorithm(self, string, context=''):
        if context == '':
            context = self.__class__.__name__
        return string, QCoreApplication.translate(context, string)

    def createInstance(self):
        return type(self)()
