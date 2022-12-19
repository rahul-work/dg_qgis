# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DGQgisPlugin
                                 A QGIS plugin
 A general tool for "Digital Geography" using QGIS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-12-19
        copyright            : (C) 2022 by GISE-Hub
        email                : rahul.work223@gmail.com
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
    """Load DGQgisPlugin class from file DGQgisPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .dg_qgis import DGQgisPlugin
    return DGQgisPlugin(iface)
