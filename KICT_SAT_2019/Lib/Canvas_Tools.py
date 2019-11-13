# -*- coding: utf-8 -*-

import os
import sys

from qgis.gui import *
from PyQt5 import QtGui
from qgis.core import *
from qgis.utils import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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
    
