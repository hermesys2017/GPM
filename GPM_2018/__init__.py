# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GPM
                                 A QGIS plugin
 GPM
                             -------------------
        begin                : 2018-06-15
        copyright            : (C) 2018 by Hermesys
        email                : mhcho058@hermesys.co.kr
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
    """Load GPM class from file GPM.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .GPM import GPM
    return GPM(iface)
