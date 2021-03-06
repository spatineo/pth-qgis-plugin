# -*- coding: utf-8 -*-
"""
/***************************************************************************
 pthplugin
                                 A QGIS plugin
 QGIS plugin utilizing the pth intelligent search api
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-11-12
        copyright            : (C) 2020 by Spatineo
        email                : patrick.alaspaa@spatineo.com
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load pthplugin class from file pthplugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .pthplugin import pthplugin
    return pthplugin(iface)
