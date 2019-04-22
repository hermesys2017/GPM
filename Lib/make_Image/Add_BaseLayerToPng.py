# -*- coding: utf-8 -*-
'''
Created on 2018. 12. 12.

별도의 캔버스, 레이어가 올라가지 않아도 OK인 방식으로

@author: MHCHO
'''
import os
from PyQt4.QtGui import QImage, QPainter
from PyQt4.QtCore import QSize

class savePNG_Addbase:
    def __init__(self,canvas, raster, polygon, line, point, savePath):
        self.canvas = canvas
        self.raster=raster
        self.polygon = polygon
        self.line = line
        self.point = point
        self.savePath = savePath
    
    
    #========== base shp 3개 ===========
    def base3_savePng(self):
        baseLayer_point = QgsVectorLayer(self.point, (os.path.basename(self.point)).split(".shp")[0], "ogr")
        baseLayer_line = QgsVectorLayer(self.line, (os.path.basename(self.line)).split(".shp")[0], "ogr")
        baseLayer_polygon = QgsVectorLayer(self.polygon, (os.path.basename(self.polygon)).split(".shp")[0], "ogr")
        QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer, baseLayer_polygon, baseLayer_line, baseLayer_point], False)
        list_layer = [baseLayer_line, baseLayer_point, baseLayer_polygon, self.rasterLayer]  # base layer가 위에
        self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_polygon),QgsMapCanvasLayer(baseLayer_line),QgsMapCanvasLayer(baseLayer_point),QgsMapCanvasLayer(self.rasterLayer)])
        self.gpm_canvas.zoomToFullExtent()
        print "base 3개"
    
    #========== base shp 2개 : Polygon, Line ===========
    def base2_savePng_1(self):
        baseLayer_line = QgsVectorLayer(self.line, (os.path.basename(self.line)).split(".shp")[0], "ogr")
        baseLayer_polygon = QgsVectorLayer(self.polygon, (os.path.basename(self.polygon)).split(".shp")[0], "ogr")
        QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer, baseLayer_polygon, baseLayer_line], False)
        list_layer = [baseLayer_line, baseLayer_point, baseLayer_polygon, self.rasterLayer]  # base layer가 위에
        self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_polygon),QgsMapCanvasLayer(baseLayer_line),QgsMapCanvasLayer(baseLayer_point),QgsMapCanvasLayer(self.rasterLayer)])
        self.gpm_canvas.zoomToFullExtent()
        print "base 3개"
    
    
    def savePng_base(self,canvas,raster,vector, saveName):
        width = 800
        height = 600
        
        dpi = 92
        img = QImage(QSize(width,height),QImage.Format_RGB32)
        img.setDotsPerMeterX(dpi/25.4*1000)
        img.setDotsPerMeterY(dpi/25.4*1000)
        
#         layers = [layer.id() for layer in iface.legendInterface().layers()]
        # layers = QgsRasterLayer("D:/Working/Gungiyeon/GPM/GPM_test/T20181211/shp/3B-HHR-L.MS.MRG.3IMERG.20170630-S000000-E002959.0000.V04B_precipitationCal_Convert_Clip.tif")
        # raster =""
        # baseLayer = "D:/Working/Gungiyeon/GPM/GPM_test/T20181211/polyline/polyLine.shp"
#         raster ="D:/Working/Gungiyeon/GPM/GPM_test/T20181211/shp/3B-HHR-L.MS.MRG.3IMERG.20170630-S000000-E002959.0000.V04B_precipitationCal_Convert_Clip.tif"
        r_lyr = QgsRasterLayer(raster,((os.path.basename(raster)).split(".png")[0]),"gdal")
#         vector = "D:/Working/Gungiyeon/GPM/GPM_test/T20181211/polyline/polyLine.shp"
        baseLayer = QgsVectorLayer(vector,(os.path.basename(vector)).split(".shp")[0],"ogr")
        QgsMapLayerRegistry.instance().addMapLayers([r_lyr,baseLayer], False)
        
        list_layer = [r_lyr,baseLayer]
        layers = [layer.id() for layer in list_layer]
        
        extent = canvas.extent()
        
        mapSettings = QgsMapSettings()
        mapSettings.setMapUnits(0)
        mapSettings.setExtent(extent)
        mapSettings.setOutputDpi(dpi)
        mapSettings.setOutputSize(QSize(width,height))
        mapSettings.setLayers(layers)
        mapSettings.setFlags(QgsMapSettings.Antialiasing|QgsMapSettings.UseAdvancedEffects
                             |QgsMapSettings.ForceVectorOutput| QgsMapSettings.DrawLabeling)
        
        p = QPainter()
        p.begin(img)
        mapRender =  QgsMapRendererCustomPainterJob(mapSettings, p)
        mapRender.start()
        mapRender.waitForFinished()
        p.end()
        
#         saveName = "D:/Working/Gungiyeon/GPM/GPM_test/T20181213/test.png"
        img.save(saveName,'png')