# -*- coding: utf-8 -*-

"""
/***************************************************************************
    ptm4qgis.py
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

import os
import sys
import inspect

from qgis.core import QgsProcessingAlgorithm, QgsApplication
from .ptm4qgis_provider import PTM4QgisProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class PTMPlugin(object):

    def __init__(self, iface):
        self.provider = None
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = PTM4QgisProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
