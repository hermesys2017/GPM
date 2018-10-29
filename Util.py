# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from subprocess import call
import sys
import os
import os.path
from subprocess import Popen
from os import listdir
import re
from qgis.core import QgsMapLayerRegistry
reload(sys)
sys.setdefaultencoding('utf-8')

class util:
    def __init__(self):
        self.tauDEMCommand = self.enum('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7')

    def enum(*sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        reverse = dict((value, key) for key, value in enums.iteritems())
        enums['reverse_mapping'] = reverse
        return type('Enum', (), enums)

    # Taudem path 받아 오기
    def GetTaudemPath(self):
        tauPath = "C:\\Program Files\\TauDEM\\TauDEM5Exe\\"
        return tauPath

    def Execute(self, arg):
        value = call(arg)
        return value
    
    def Excute_test(self):
        arg = "C:/Program Files/GDAL/gdal_calc.py -A C:/GRM/inha/band1.tif --outfile=C:/GRM/inha/output.tif --calc=A*logical_or(A<=7,A>=5) --NoDataValue = 0"
        # call([sys.executable, 'C:/PROGRA~2/GDAL/gdal_calc.py', '-A', 'C:/GRM/inha/band1.tif', '--outfile=C:/GRM/inha/output.tif','--calc=A+1'])
        self.MessageboxShowError("test",arg)
        os.system(arg)
        # call(arg)

    # 윈도우 임시 폴더에 임시 파일 생성
    def GetTempFilePath(self, tempfilepath):
        output_temp = win32api.GetTempPath() + os.path.basename(tempfilepath)
        output_temp = output_temp.replace('\\', '\\\\')
        return output_temp

    # 콤보박스 리스트 셋팅 type은( tif, shp , "" 일땐 모두다)
    def SetCommbox(self, layers, commbox, type):
        layer_list = []
        if type.upper() == "TIF" or  type.upper() == "ASC" :
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.RasterLayer:
                    layer_list.append(layer.name())
        elif type.upper() == "SHP":
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.VectorLayer:
                    layer_list.append(layer.name())
        else:
            for layer in layers:
                layer_list.append(layer.name())
        commbox.clear()
        combolist = ['select layer']
        combolist.extend(layer_list)
        commbox.addItems(combolist)

    # 메시지 박스 출력
    def MessageboxShowInfo(self, title, message):
        QMessageBox.information(None, title, message)

    def MessageboxShowError(self, title, message):
        QMessageBox.warning(None, title, message)

    # 콤보 박스에서 선택된 레이어 경로 받아 오기
    def GetcomboSelectedLayerPath(self, commbox):
        layername = commbox.currentText()
        if layername == 'select layer':
            return ""
        else:
            layer = None
            for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                if lyr.name() == layername:
                    layer = lyr
            return layer.dataProvider().dataSourceUri()


     # 레이어 명으로 경로 받아 오기
    def GetTxtToLayerPath(self, layernametxt):
        layername = layernametxt
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
        if layer != None :
            return layer.dataProvider().dataSourceUri()
        else :
            return "Null"

    def GetLayerPath(self, layername):
        layername = layername
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
        return layer.dataProvider().dataSourceUri()




    # 파일 존재 유무 확인
    def CheckFile(self, path):
        filepath = path.replace('\\', '\\\\')
        if (os.path.isfile(filepath)):
            return True
        else:
            return False

    # 폴더 경로 맞는지 확인
    def CheckFolder(self, path):
        filepath = path.replace('\\', '\\\\')
        if (os.path.isdir(filepath)):
            return True
        else:
            return False

    def CheckTaudem(self):
        if os.path.isdir('C:\\Program Files\\TauDEM'):
            return True
        else:
            return False


    # 폴더및 파일 명칭에 한글 포함하고 있는지 체크
    def CheckKorea(self,string):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        strs = re.sub('[^가-힣]', '', string.decode('utf-8').encode('utf-8'))
        if len(strs)>0:
            return True
        else :
            return False

    # 라벨, 타입으로 구분
    def GlobalLabel(self, label, type):
        if type.upper() == "COLROW":
            self.label1 = label
       
    # 라벨, 타입으로 구분
    def GlobalEdit(self, edit, type):
        if type.upper() == "CW":
            self.edit = edit

    # 라벨 텍스트,타입으로 구분
    def GlobalLabel_SetText(self, mess, type):
        if type.upper() == "COLROW":
            self.label1.setText(mess)


    # 라벨 텍스트,타입으로 구분
    def GlobalEdit_SetText(self, mess, type):
        if type.upper() == "CW":
            self.edit.setText(mess)

    def Opewn_ViewFile(self,path):
        _notpad = "C:/Windows/System32/notepad.exe"
        Popen([_notpad,path])

    #def GetFileName(self,path):
    #    name =os.path.basename(path)
    #    a=os.path.splitext(path)[1]
    #    return name.replace(a,"")

    # 파일 경로 중에 파일명만 받아 오기
    def GetFilename(self,filename):
        s = os.path.splitext(filename)
        s = os.path.split(s[0])
        return  s[1]

    # 폴더 내부에 있는 파일 목록 리스트화 하기
    def GetFilelist(self,directory, extension):
        filelist = []
        for file in os.listdir(directory):
            if file.lower().endswith("."+ extension):
                filelist.append(directory +"/" +file)
        return filelist

    def ConvertRasterToASC(self,inputFileName,  outputFileName):
#         arg = "C:/Program Files/QGIS 2.18/bin/gdal_translate.exe"
        arg = "gdal_translate.exe"
        arg  = arg  +  " -of AAIGrid " + inputFileName + " " + outputFileName
        self.Execute(arg)

    def ExecuteGridResampling(self,method,cellSize,inputfilename,outputfilename):
#         arg = "C:/Program Files/QGIS 2.18/bin/gdalwarp.exe"
        arg = "gdalwarp.exe"
        arg =arg +  " -r " + method +" -tr " + cellSize +  " " + cellSize + " "+ inputfilename + " "+ outputfilename
        self.Execute(arg)

    def ConvertShapeToCSV(self,inputFileName,  outputFileName):
#         arg = "\"" + "C:/Program Files/GDAL/ogr2ogr.exe" + "\""
#         arg="\"" + "C:/Program Files/QGIS 2.18/bin/ogr2ogr.exe" + "\""
        arg = "ogr2ogr.exe"
        arg = arg + " -f CSV " + "\"" + outputFileName + "\" " + "\"" + inputFileName + "\" -lco GEOMETRY=AS_XYZ"
        self.Execute(arg)

    def ConvertUTM(self,inputFileName,  outputFileName,s_srs,t_srs):
#         arg = "\"" + "C:/Program Files/GDAL/gdalwarp.exe" + "\""
        arg = "gdalwarp.exe"
        arg = arg + " -s_srs " + "\"" + s_srs + "\"" + " -t_srs " + "\"" + t_srs + "\" " + "\"" + inputFileName + "\" " + "\"" + outputFileName + "\""
        self.Execute(arg)

     # 콤보박스 리스트 셋팅 type은( tif, shp , "" 일땐 모두다)
    def SetCommbox(self, layers, commbox, type):
        layer_list = []
        if type.upper() == "TIF":
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.RasterLayer:
                    layer_list.append(layer.name())
        elif type.upper() == "SHP":
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.VectorLayer:
                    layer_list.append(layer.name())
        elif type.upper() == "ASC":
            for layer in layers:
                layertype = layer.type()
                if layertype == layer.RasterLayer:
                    layer_list.append(layer.name())
        else:
            for layer in layers:
                layer_list.append(layer.name())
        commbox.clear()
        combolist = ['select layer']
        combolist.extend(layer_list)
        commbox.addItems(combolist)

    def Qgis_Layer_list(self, layers):
        layer_list = []
        for layer in layers:
            layertype = layer.type()
            if layertype == layer.RasterLayer:
                layer_path=layer.dataProvider().dataSourceUri()
                fname, ext = os.path.splitext(layer_path)
                if ext.upper()==".ASC":
                    layer_list.append(layer.dataProvider().dataSourceUri())
                    # layer_list.append(layer.name())
        return  layer_list


    # 메시지 박스 출력
    def MessageboxShowInfo(self, title, message):
        QMessageBox.information(None, title, message)

    def MessageboxShowError(self, title, message):
        QMessageBox.warning(None, title, message)

    # 콤보 박스에서 선택된 레이어 경로 받아 오기
    def GetcomboSelectedLayerPath(self, commbox):
        layername = commbox.currentText()
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == layername:
                layer = lyr
        return layer.dataProvider().dataSourceUri()

    # 파일 존재 유무 확인
    def CheckFile(self, path):
        filepath = path.replace('\\', '\\\\')
        if (os.path.isfile(filepath)):
            return True
        else:
            return False

    # 폴더 경로 맞는지 확인
    def CheckFolder(self, path):
        filepath = path.replace('\\', '\\\\')
        if (os.path.isdir(filepath)):
            return True
        else:
            return False

    # 폴더및 파일 명칭에 한글 포함하고 있는지 체크
    def CheckKorea(self,string):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        strs = re.sub('[^가-힣]', '', string.decode('utf-8').encode('utf-8'))
        if len(strs)>0:
            return True
        else :
            return False

    def Execute(self, arg):
        CREATE_NO_WINDOW = 0x08000000
        value = call(arg, creationflags=CREATE_NO_WINDOW)
        return value
    

        