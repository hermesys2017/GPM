# -*- coding: utf-8 -*-

from qgis.gui import QgsMapTool, QgsMapToolPan
from qgis.PyQt.QtWidgets import QAction


class Canvas_Tools(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas

    def ZoomtoExtent(self):
        self.canvas.zoomToFullExtent()
        self.canvas.refresh()

    def canvas_pan(self):
        actionPan = QAction(self)
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(actionPan)
        self.canvas.setMapTool(self.toolPan)
