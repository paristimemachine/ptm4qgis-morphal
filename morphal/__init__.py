# -*- coding: utf-8 -*-

"""
/***************************************************************************
    PTM4Qgis
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Eric Grosso'
__date__ = 'January 2021'
__copyright__ = '(C) 2021, Eric Grosso, Paris Time Machine'

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PTMPlugin class from file ptm4qgis.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from ptm4qgis.ptm4qgis import PTMPlugin
    # return PTMPlugin()  # if no UI
    return PTMPlugin(iface)
