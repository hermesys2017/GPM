# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GPMDialog
                                 A QGIS plugin
 GPM
                             -------------------
        begin                : 2018-06-15
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Hermesys
        email                : mhcho058@hermesys.co.kr
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

import os,sys,shutil
import sys
from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import subprocess as sub
import processing
import GPM
import Util as util
import Dict
import GPM
import csv
from PyQt4.QtGui import QFileDialog


sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+'/Lib')
import imageio
import OneFileCorrection_class as OneFile
import coordinate_class
import util_accum
import time
from time import time, sleep
import ProgressBar
import wget

_iface ={}
# 2018-08-06 박: 기능 테스트로 임시 추가 
# function 기능으로 추가 테스트중
import qgis
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from PyQt4.QtGui import QProgressDialog, QProgressBar
#from Scripts.gdal_calc import Calc

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GPM_dialog_base.ui'))

path = os.path.dirname(os.path.realpath(__file__))
settings_icon = path +'\image\settings.png'
_util = util.util()
_layers = {}
_Dict = Dict.dict()


'''
2018-09-09 JO:
csv 파일 변환하는 함수에서 _coord 로 해둔 부분이 있음.
해당 부분은 장소 명을 좌표로 바꾸는 부분임.
옮겨쓰는 과정에서 지워졌나봄. 상단에  import만 되어 있음.
2018-06 버전에서는 해당 부분이 있음.
'''
_coord = coordinate_class.place_to_coordinate()
_corr=OneFile.satellite_correction()
_utilAC = util_accum.accum_util()

os.environ['GDAL_DATA'] = os.popen('gdal-config --datadir').read().rstrip()
bin_directory = r"C:/Program Files/QGIS 2.18/OSGeo4W.bat"
os.environ['PATH'] += os.path.pathsep + bin_directory
osgeo4w="C:/Program Files/QGIS 2.18/OSGeo4W.bat"


cursor=0

_ASC_filename=[]
_CSV_filename=[]
select_file=[]
_PNG_filename=[]

# gdal_path = os.path.dirname(os.path.abspath(__file__))+"/Lib/gdal/gdal/apps/"
# /GPM/Lib/gdal/gdal/apps/gdal_translate.exe

class GPMDialog(QtGui.QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GPMDialog, self).__init__(parent)
        self.setupUi(self)

        # 초기 설정
        self.Setini()

        # Clip 영역 테이블 레이어 셋팅
#         self.Set_Clip_table_layerlist()
        
        #--------------연대 모듈------------------------------------------

         # Qgis 레이어 목록
        global _ASC_filename
        layers = GPM._iface.legendInterface().layers()
        _ASC_filename=_util.Qgis_Layer_list(layers)

        # 2018-06-11 박: 테이블 헤더 기본 셋팅
        self.SetTable_header()
        # 2018 -05-08 : 프로그램 수정
        # 라디오 버튼 기본 설정

        self.rdo_Layer.setChecked(True)

        self.rdo_Layer.toggled.connect(self.Select_radio_event)

        self.rdo_Files.toggled.connect(self.Select_radio_event)

        self.Select_radio_event()

        #사용자가 ASC 파일 선택 이벤트
        self.btnOpenDialog_Input.clicked.connect(self.Select_ASC_event)

        # CSV 파일 선택 이벤트
        self.btn_Select_Covert_File.clicked.connect(self.Select_CSV_event)

        # Convert 버튼 이벤트
        self.btn_Covert.clicked.connect(self.Convert_CSV_event)

        # btn_Apply 버튼 이벤트 모든 리스트 파일이 있을때 작동
#         self.btn_Apply.clicked.connect(self.Apply_AllList_event)
        self.btn_Apply.clicked.connect(self.Apply_all_correction)

        #decimal 숫자 초기화(항상 0부터 시작하도록, 초기화)
        self.decimalBox.setValue(0)
        
        #프로그램 종료
        #self.btnClose.clicked.connect(self.Close_Form)
        
        #버튼 아이콘 설정
        self.set_btn_icon()

        #사용자가 output 다이얼로그를 눌렀을 때 이벤트 처리
        self.btnOutputDialog.clicked.connect(self.Output_path_Dialog)

        #OK 버튼 누르면 Satellite correction이 수행됨
        #self.btnOK.clicked.connect(self.run_Result)

        #Result load to canvas 버튼 기본 체크 상태
        self.chk_AddLayer.setChecked(True)
        #Make PNG 체크박스는 기본 체크 상태
        self.chk_makePng.setChecked(True)



        # 멀티 셀렉트 옵션 
        self.tbl_asc_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.btl_png_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # Interval_box. duration 조절, GIF의 속도를 조절. 초기값은 0.5 기본 값으로 셋팅
#         self.Interval_box.setValue(0.5)

        # 2018-06-11 박: 
        self.btn_csvUp.clicked.connect(lambda : self.MoveUp(self.lisw_Convert_file))
        self.btn_csvDown.clicked.connect(lambda: self.MoveDown(self.lisw_Convert_file))
        self.btn_csvRemove.clicked.connect(lambda: self.ReMove(self.lisw_Convert_file))

        self.btn_ASCup.clicked.connect(lambda : self.MoveUp(self.lisw_ASC))
        self.btn_ASCdown.clicked.connect(lambda: self.MoveDown(self.lisw_ASC))
        self.btn_ASCremove.clicked.connect(lambda: self.ReMove(self.lisw_ASC))

        # GIF 만들기
#         self.btn_makeGIF.clicked.connect(self.make_gif)
#         self.btn_save_gif_path.clicked.connect(self.Save_gif_path)
        self.btn_select_asc_files.clicked.connect(lambda:self.Folder_List("ASC"))
        self.btn_make_png_files.clicked.connect(self.Make_png_menu)
        self.btn_select_png_Folder.clicked.connect(lambda:self.Folder_List("PNG"))
        self.btn_select_save_path_imag.clicked.connect(lambda:self.saveFileDialog("GIF"))
        self.btn_make_gif_file.clicked.connect(self.Make_gif_user)
        #--------------------연대 모듈 끝-------------------------------------------
       








    def Setini(self):
        global _layers
        _layers = GPM._iface.legendInterface().layers()
        
        #wget_data download
        self.btn_bat_path.clicked.connect(self.wget_save_path)
        self.btn_datadownload.clicked.connect(self.wget_create_bat)

        # 클립 영역 선택 콤보 박스 셋팅 (한반도 , 남한 영역, 필리핀, 모로코 영역)
        self.cmb_clip_zone.addItems(["Select Country","Korea","South_Korea","Philippines","Morocco", "Korea_Typoon"])
#         self.cmb_utm_source.addItems(["Select UTM","WGS84_UTM 28N","WGS84_UTM 29N","WGS84_UTM 30N","WGS84_UTM 50N","WGS84_UTM 51N","WGS84_UTM 52N","WGS84_UTM 53N"])
        self.cmb_utm_target.addItems(["Select UTM", 
                                      'WGS84_UTM 1N','WGS84_UTM 1S','WGS84_UTM 2N','WGS84_UTM 2S','WGS84_UTM 3N','WGS84_UTM 3S','WGS84_UTM 4N','WGS84_UTM 4S','WGS84_UTM 5N','WGS84_UTM 5S',
                                      'WGS84_UTM 6N','WGS84_UTM 6S','WGS84_UTM 7N','WGS84_UTM 7S','WGS84_UTM 8N','WGS84_UTM 8S','WGS84_UTM 9N','WGS84_UTM 9S','WGS84_UTM 10S','WGS84_UTM 11N',
                                      'WGS84_UTM 11S','WGS84_UTM 12N','WGS84_UTM 12S','WGS84_UTM 13N','WGS84_UTM 13S','WGS84_UTM 14N','WGS84_UTM 14S','WGS84_UTM 15N','WGS84_UTM 15S','WGS84_UTM 16N','WGS84_UTM 16S',
                                      'WGS84_UTM 17N','WGS84_UTM 17S','WGS84_UTM 18N','WGS84_UTM 18S','WGS84_UTM 19N','WGS84_UTM 19S','WGS84_UTM 20N','WGS84_UTM 20S','WGS84_UTM 21N','WGS84_UTM 21S','WGS84_UTM 22N',
                                      'WGS84_UTM 22S','WGS84_UTM 23N','WGS84_UTM 23S','WGS84_UTM 24N','WGS84_UTM 24S','WGS84_UTM 25N','WGS84_UTM 25S','WGS84_UTM 26N','WGS84_UTM 26S','WGS84_UTM 27N','WGS84_UTM 27S',
                                      'WGS84_UTM 28N','WGS84_UTM 28S','WGS84_UTM 29N','WGS84_UTM 29S','WGS84_UTM 30N','WGS84_UTM 30S','WGS84_UTM 31N','WGS84_UTM 31S','WGS84_UTM 32N','WGS84_UTM 32S','WGS84_UTM 33N',
                                      'WGS84_UTM 33S','WGS84_UTM 34N','WGS84_UTM 34S','WGS84_UTM 35N','WGS84_UTM 35S','WGS84_UTM 36N','WGS84_UTM 36S','WGS84_UTM 37N','WGS84_UTM 37S','WGS84_UTM 38N','WGS84_UTM 38S',
                                      'WGS84_UTM 39N','WGS84_UTM 39S','WGS84_UTM 40N','WGS84_UTM 40S','WGS84_UTM 41N','WGS84_UTM 41S','WGS84_UTM 42N','WGS84_UTM 42S','WGS84_UTM 43N','WGS84_UTM 43S','WGS84_UTM 44N',
                                      'WGS84_UTM 44S','WGS84_UTM 45N','WGS84_UTM 45S','WGS84_UTM 46N','WGS84_UTM 46S','WGS84_UTM 47N','WGS84_UTM 47S','WGS84_UTM 48N','WGS84_UTM 48S','WGS84_UTM 49N','WGS84_UTM 49S',
                                      'WGS84_UTM 50N','WGS84_UTM 50S','WGS84_UTM 51N','WGS84_UTM 51S','WGS84_UTM 52N','WGS84_UTM 52S','WGS84_UTM 53N','WGS84_UTM 53S','WGS84_UTM 54N','WGS84_UTM 54S','WGS84_UTM 55N',
                                      'WGS84_UTM 55S','WGS84_UTM 56N','WGS84_UTM 56S','WGS84_UTM 57N','WGS84_UTM 57S','WGS84_UTM 58N','WGS84_UTM 58S','WGS84_UTM 59N','WGS84_UTM 59S','WGS84_UTM 60N','WGS84_UTM 60S'])
        
#         self.cmb_resample_method.addItems(["Select Method","near","bilinear","cubic","cubicspline","lanczos","average","mode","max","min","med","q1","q3"])
        self.cmb_resample_method.addItems(["bilinear","near","cubic","cubicspline","lanczos","average","mode","max","min","med","q1","q3"])
        
        
        # 라디오 버튼 초기화
        self.rdo_Combo_Clip.setChecked(True)
        self.Rdo_Selected()

        # 라디오 버튼 이벤트 처리
        self.rdo_Combo_Clip.clicked.connect(self.Rdo_Selected)
        self.rdo_Shape_Clip.clicked.connect(self.Rdo_Selected)

        # Shape 파일 경로 받아 오기
        #self.btn_shape_dialog.clicked.connect(lambda :self.Shape_Select(self.txt_Shape_path))

        # 폴더 선택 다이얼로그
        self.btn_Output_Folder.clicked.connect(lambda :self.Select_Folder_Dialog(self.txt_output_clip))

        #2018-09-03=================
        #convert Apply 버튼 클릭 인벤트
        #김주훈 박사님과 협의 사항으로 기능을 병합 하기로함
        
        #2018-10-15 추가 ========
        self.btn_input_hdf5.clicked.connect(self.select_hdf5)
        self.txt_hdf5_inPath.setText("Grid")
        self.txt_hdf_inName.setText("precipitationCal")
        #2018-10-15 End
        
        
        self.btn_Apply_Convert.clicked.connect(self.Convert_hdf5)
        self.Set_Convert_table_layerlist()
        self.btn_Output_Folder_Convert.clicked.connect(lambda :self.Select_Folder_Dialog(self.txt_Output_Convert))
        #============================

        # 클립 영역 Apply 버튼 클릭 이벤트
        self.btn_input_tiff.clicked.connect(self.select_Cilp_files)
        self.btn_apply_clip.clicked.connect(self.Clip_apply_Click)

        # 트리 위젯셋팅
        self.Set_treeWidget()

        self.txt_Convert_EX.setText(" Extract from HDF5 rasterml Transpose function ")
        self.txt_Clip_EX.setText(" Clip to user specified area ")
        self.txt_UTM_EX.setText(" WGS84 Provides UTM conversion function for latitude and longitude ")

        # UTM
        self.btn_input_utm.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_input_utm))
        self.btn_output_utm.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_output_utm))
        self.btn_apply_utm.clicked.connect(self.UTM_apply_Click)

        # resample
        self.btn_input_resample.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_input_resample))
        self.btn_output_resample.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_output_resample))
        self.btn_apply_resample.clicked.connect(self.Resample_apply_Click)

        # Accum
#         self.rdo_Accum_1H.setChecked(True)
#         self.chk_All_Check.setChecked(True)
        self.btn_input_accum.clicked.connect(self.select_files)
        #self.btn_input_accum.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_input_accum))

        self.btn_output_accum.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_output_accum))
        # self.btn_shp_accum.clicked.connect(lambda: self.Save_File_Dialog(self.txt_reference_shp,"shp"))
        
        self.btn_apply_accum.clicked.connect(self.Accum_apply_Click)
        
        # convert CSV
#         self.txt_fieldname_shp.setText("u_id")
        self.btn_csv_shp.clicked.connect(lambda: self.Shape_Select(self.txt_csv_shp))
        self.btn_csv_csv.clicked.connect(lambda: self.Save_File_Dialog(self.txt_shp_field,"csv"))
#         (lambda: self.Save_File_Dialog(self.txt_shp_field,"shp"))
        self.btn_raster_tiff.clicked.connect(self.raster_tiff_select)
        self.btn_apply_CSV.clicked.connect(self.CSV_apply_Click)
         
        # function 
#         self.btn_input_function.clicked.connect(self.select_files_func)
        self.btn_apply_Function.clicked.connect(self.Fun_apply_Click)
        # 테이블 데이터 셋팅
        self.Set_table_list_fun()
         
        # Make ASC
        self.txt_input_asc.setEnabled(False) #only 버튼을 클릭하여 파일 선택할 수 있음
        self.btn_input_asc.clicked.connect(self.select_ASC_files)
#             lambda: self.Select_File_Dialog(self.txt_input_asc))
        self.btn_output_asc.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_output_asc))
#             lambda: self.Save_File_Dialog(self.txt_output_asc,"asc"))
        self.btn_apply_ASC.clicked.connect(self.ASC_apply_Click)
        
        # Make image
        self.btn_output_png.clicked.connect(lambda :self.Select_Folder_Dialog(self.txt_output_png))
        
    #★★★★★★★★★★★★★★★★★★★★★★★  2018-08-20 ★★★★★★★★★★★★★★★★★★★
#         self.tlb_Function.doubleClicked.connect(self.double_click)
#         self.txt_function_txt.cursorPositionChanged.connect(self.txtFuntion)
#         self.btn_input_Function.clicked.connect(lambda:self.saveFileDialog("TIF"))
        self.txt_function_txt.setText("x+1")
        self.btn_input_Function.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_output_fun)) #폴더 선택으로 변경
    
    #저장 경로 입력 받기 
    def saveFileDialog(self,type):
        if type.upper()=="TIF":
            file = str(QFileDialog.getSaveFileName(self, "Save Folder Path", "C://", ".tif"))
            self.txt_output_fun.setText(file)
        else:
            file = str(QFileDialog.getSaveFileName(self, "Save GIF Path", "C://", ".gif"))
            self.txt_save_gif_path_imag.setText(file)
    
    #txt_function_txt에서 현재 커서의 위치를 반환하기
    def txtFuntion(self):
        global cursor
        cursor=self.txt_function_txt.cursorPosition()

    #더블 클릭시 txt_function_txt에 클릭한 레이어 이름을 커서 위치에 삽입
    def double_click(self):
        try:
            row=self.tlb_Function.currentRow()
            item=self.tlb_Function.item(row,0).text()
            
            self.txt_function_txt.setText(self.txt_function_txt.text()[:cursor]+"\"" +item + "\""+self.txt_function_txt.text()[cursor:])
            
        except Exception as e:
            _util.MessageboxShowError("Flood",str(e))
    
    #★★★★★★★★★★★★★★★ ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    # ===============Convert==============================================
    def Set_Convert_table_layerlist(self):
        self.tb_hdf5.setColumnCount(1)
        self.tb_hdf5.setHorizontalHeaderLabels(["Layer List"])

        stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
        self.tb_hdf5.setStyleSheet(stylesheet)
        count=0
        # 레이어 데이터 경로 받아서 배열에 미리 넣어 두기
        self.layer_Data=[]
        self.layer_Name=[]
        #2018-10-15 잠시 보류
#         for layer in _layers:
#             self.tb_hdf5.insertRow(count)
#             self.tb_hdf5.setItem(count, 0, QTableWidgetItem(layer.name()))
#             self.layer_Data.append(str(layer.dataProvider().dataSourceUri()))
#             self.layer_Name.append(layer.name())
#             count = count+1
            

    # =============== Clip ===============================================
    # 테이블에 레이어 목록을 셋팅 하기
    def Set_Clip_table_layerlist(self):
        self.tb_clip_Tiff.clear() #초기화
        self.tb_clip_Tiff.setRowCount(0)
        
        self.tb_clip_Tiff.setColumnCount(1)
        self.tb_clip_Tiff.setHorizontalHeaderLabels(["Layer List"])
        stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
        self.tb_clip_Tiff.setStyleSheet(stylesheet)
        count = 0
        
        
        
        #불편해서 프로그레스바 추가함. 힘들다
        self.clip_progressBar.setValue(0)
        
        for layer in (self.hdf_convert_tiff):
            self.tb_clip_Tiff.insertRow(count)
#             self.tb_clip_Tiff.setItem(count, 0, QTableWidgetItem(layer.name()))
            self.tb_clip_Tiff.setItem(count, 0, QTableWidgetItem(layer))
            count=count+1
            
        
        #2018-10-15 잠시 보류
#         for layer in _layers:
#             self.tb_clip_Tiff.insertRow(count)
#             self.tb_clip_Tiff.setItem(count, 0, QTableWidgetItem(layer.name()))
#             count=count+1
         # 테이블 데이터 수정 못하게 옵션
        self.tb_clip_Tiff.setEditTriggers(QTableWidget.NoEditTriggers)
        

    def Rdo_Selected(self):
        if self.rdo_Combo_Clip.isChecked():
            self.cmb_clip_zone.setEnabled(True)
            #self.txt_Shape_path.setEnabled(False)
            #self.btn_shape_dialog.setEnabled(False)
        else:
            self.cmb_clip_zone.setEnabled(False)
            #self.txt_Shape_path.setEnabled(True)
            #self.btn_shape_dialog.setEnabled(True)

    def Shape_Select(self,txt):
        fname = QFileDialog.getOpenFileName(self, 'Open file','c:/', "Shpae files (*.shp)")
        if _util.CheckFile(fname):
            txt.setText(fname)

    def Select_Folder_Dialog(self,txt):
        Folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if _util.CheckFolder(Folder):
            txt.setText(Folder)

    # 파일 선택 다이얼 로그 나중에 Util 파일로 변경해야함
    def Select_File_Dialog(self, txt):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'select output file', '','GRM Project xml files (*.tif)',options=QtGui.QFileDialog.DontUseNativeDialog)
        txt.setText(filename)

    def  Save_File_Dialog(self,txt,type):
        try:
            if type=="asc":
                filename =  QtGui.QFileDialog.getSaveFileName(self, 'save file','c:/', filter ="asc (*.asc *.)")
                txt.setText(filename)
            elif type == "shp":
                filename = QtGui.QFileDialog.getSaveFileName(self, 'save file', 'c:/', filter="shp (*.shp *.)")
                txt.setText(filename)
            elif type=="csv":
                filename = QtGui.QFileDialog.getSaveFileName(self, 'save file', 'c:/', filter="csv (*.csv *.)")
                txt.setText(filename)
        except Exception as se:
            _util.MessageboxShowInfo("GPM", str(se))
    
    def raster_tiff_select(self):
        self.filenames = QFileDialog.getOpenFileNames(self, 'Open file','c:/', 'GRM Project xml files (*.tif)')
        self.txt_raster_tiff.setText(str(self.filenames))
#         QFileDialog.getOpenFileNames(self,"Select Input ASC FILES",dir,"*.asc *.ASC ",options=QtGui.QFileDialog.DontUseNativeDialog)
    

    #============HDF5TOTIFF APPLY================
    def select_hdf5(self):
        try:
            self.tb_hdf5.clear() #초기화
            self.tb_hdf5.setRowCount(0)
            self.hdf5_progressBar.setValue(0)
            
            filter = "HDF5 (*.RT-H5)"
            file_name = QtGui.QFileDialog()
            file_name.setFileMode(QFileDialog.ExistingFiles)
            files = file_name.getOpenFileNamesAndFilter(self, "Open files", "C:\\", filter)
            FileList = files[0]

            self.tb_hdf5.setColumnCount(1)
            self.tb_hdf5.setHorizontalHeaderLabels(["Layer List"])
            stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
            self.tb_hdf5.setStyleSheet(stylesheet)
            count=0
            
            self.hdf5_list = []
            for file in FileList:
                self.tb_hdf5.insertRow(count)
                self.tb_hdf5.setItem(count, 0, QTableWidgetItem(str(file)))
                self.hdf5_list.append(str(file))
                
#                 count+=1
                count = count + 1
            
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))
    
    
    def Convert_hdf5(self):
        try:
            
            foldersss = self.txt_Output_Convert.text()
            if foldersss.strip()=="":
                _util.MessageboxShowInfo("GPM", "The folder path is not set.")
                self.txt_Output_Convert.setFocus()
                return
            
            #2018-10-15 : 리스트에서 선택 X 파일 선택 단계에서 이미 선택한 것으로 가정
#             self.rows = []
#             if len(self.tb_hdf5.selectedIndexes()) > 0:
#                 for idx in self.tb_hdf5.selectedIndexes():
#                     self.rows.append(idx.row())
#             else:
#                 _util.MessageboxShowError("GPM", "No columns selected or no layers.")
#                 return

            # 사용자가 원하는 파일을 tiff 파일로 분리 함수
            Tiff_List=self.BandtoTiff()
            # 결과 좌표계 설정 
            self.Convert_crs_tif(self.MaketoTif)
            
#             self.Convert_utm_tif(self.MaketoTif)
            
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))
            
    # tiff 분리 하기
    def BandtoTiff(self):
        try:
            self.MaketoTif =[]
            for idx in self.hdf5_list:
#             for idx in self.tb_hdf5.selectedIndexes():
                datasouce = idx
#                 self.hdf5_list[idx.row()]
#                 QgsMessageLog.logMessage(str(datasouce),"GPM TIFF")
                name = _util.GetFilename(datasouce)
                #변환된 원본 TIFF 저장 폴더 생성
                if os.path.exists(self.txt_Output_Convert.text()+"/step1/") == False:
                    folder = self.txt_Output_Convert.text()+"/step1/"
                    os.mkdir(folder)
#                 name = self.hdf5_list[idx.row()].replace(":","_").replace("/","").replace("\"","").strip()
                self.MaketoTif.append(folder+ name + "_precipitationCal.tif")
# #                 arg = "gdal_translate.exe "  + "\"" + datasouce + "\"" + " -of GTiff "  +  "\"" + self.txt_Output_Convert.text() + "\\" + name + ".tif" + "\""
                
                
                
                output = folder+name+"_"+self.txt_hdf_inName.text()+".tif"
#                 QgsMessageLog.logMessage(str(output),"GPM TIFF output")
                try:
                    arg = "gdal_translate.exe HDF5:"+ "\"" + str(datasouce) +"\""+"://{0}/{1} -of GTiff {2}".format(self.txt_hdf5_inPath.text(),self.txt_hdf_inName.text(),output)
#                 arg = "gdal_translate.exe HDF5:"+ "\"" + str(datasouce) +"\""+"://{0}/{1} -of GTiff {2}/{3}".format(self.txt_hdf5_inPath.text(),self.txt_hdf_inName.text(),self.txt_Output_Convert.text(),name+"_"+self.txt_hdf_inName.text()+".tif" )
                    QgsMessageLog.logMessage(str(arg),"GPM TIFF")
#                 exe=_util.Execute(arg)
                    
                    os.system(arg)
                    #결과 파일이 안 만들어지면 중간에 끝내 버리도록 해버림.(어차피 없으면 진행 안됨)
                    if os.path.exists(output) == True:
                        pass
                    elif os.path.exists(output) != True:
                        _util.MessageboxShowError("GPM","Failed Create output file.")
                        self.hdf5_progressBar.setValue(0)
                        return
                    
                except Exception as e:
                    QgsMessageLog.logMessage(str(e),"GPM TIFF")
                    
            self.hdf5_progressBar.setValue(0)    
            self.hdf5_progressBar.setMaximum(len(self.MaketoTif))
            
        except Exception as e:
            _util.MessageboxShowError("Error message", str(e))
            
    
    #made in JO - 좌표계 변환... - 20180913
    def Convert_crs_tif(self, list):
        try:
            
            try:
                self.hdf_convert_tiff=[] ; hdf_pro_count=0
                for file in list:
                    #가로세로 변환된 원본 TIFF 저장 폴더 생성
                    if os.path.exists(self.txt_Output_Convert.text()+"/step2/") == False:
                        folder = self.txt_Output_Convert.text()+"/step2/"
                        os.mkdir(folder)
                        
                    filename = _util.GetFilename(file)
#                     output = folder+name+"_"+self.txt_hdf_inName.text()+".tif"
                    Output =  folder + filename+"_Convert.tif"
#                     Output = file.replace(filename, filename + "_Convert")
                    
    #                2018-09-16 JO : 원exe2 사용
                    converter_exe =  os.path.dirname(os.path.abspath(__file__))+"/Lib/kict_sra_gpm_converter\KICT_SRA_GPM_Converter.exe" 
                    sub.call([converter_exe, file, Output],shell=True)
                    #2018-10-17 : JO - output 파일이 실존하면 리스트에 추가되도록 수정함. 
                    try:
                        if (os.path.exists(Output)) == True:
                            self.hdf_convert_tiff.append(Output)
                            hdf_pro_count=hdf_pro_count+1
                            self.hdf5_progressBar.setValue(hdf_pro_count)
                            sleep(1)
                            
                        elif (os.path.exists(Output)) != True:
                        #맵윈도우가 없으면 실행이 안되니까...
                            _util.MessageboxShowInfo("GPM", "Please check Manual(Part install Mapwindow5).")
                    except Exception as e:
                        _util.MessageboxShowInfo("GPM",str(e))
                        
            except Exception as e:
                _util.MessageboxShowInfo("GPM",str(e))
            
#             self.calc((len(self.hdf_convert_tiff)*1000), (len(self.hdf_convert_tiff)*2000))
#             self.calc(len(self.hdf_convert_tiff)*5)
            #clip 준비... 2018-10-15 신설
            self.Set_Clip_table_layerlist()
        except Exception as e:
            _util.MessageboxShowError("GPM" , str(e))
    

    #========CLIP APPLY=========
    #clip 파일 지정
    def select_Cilp_files(self):
        try: 
            self.tb_clip_Tiff.clear() #초기화
            self.tb_clip_Tiff.setRowCount(0)
            self.clip_progressBar.setValue(0)
            
            filter = "tif (*.tif)"
            file_name = QtGui.QFileDialog()
            file_name.setFileMode(QFileDialog.ExistingFiles)
            files = file_name.getOpenFileNamesAndFilter(self, "Open files", "C:\\", filter)
            FileList = files[0]

            self.tb_clip_Tiff.setColumnCount(1)
            self.tb_clip_Tiff.setHorizontalHeaderLabels(["Layer List"])
            stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
            self.tb_clip_Tiff.setStyleSheet(stylesheet)
            count=0
            
            self.hdf_convert_tiff = []
            for file in FileList:
                self.tb_clip_Tiff.insertRow(count)
                self.tb_clip_Tiff.setItem(count, 0, QTableWidgetItem(str(file)))
                self.hdf_convert_tiff.append(str(file))
                
#                 count+=1
                count = count + 1
            #프로그레스바 신설.. 내가 불편해서 만들었음
            self.acc_progressBar.setValue(0)
            
                
        except Exception as e:
            _util.MessageboxShowInfo("GPM",str(e))
    
    
    
    #clip apply
    def Clip_apply_Click(self):
        os.environ['GDAL_DATA']='C:\Program Files\QGIS 2.18\share'
        try:
            #clip zone comboBox 지정 여부 확인
            if self.rdo_Combo_Clip.isChecked():
                if self.cmb_clip_zone.currentIndex() ==0 :
                    _util.MessageboxShowInfo("GPM" ,"Not selected Country")
                    self.cmb_clip_zone.setFocus()
                    return
            #else:
            #    Path_txt=self.txt_Shape_path.text()
            #    if Path_txt.strip()=="":
            #        _util.MessageboxShowInfo("GPM","The file path is not set.")
            #        self.txt_Shape_path.setFocus()
            #        return
            
            #결과 파일 출력 경로 지정 여부 확인
            foldersss = self.txt_output_clip.text()
            if foldersss.strip()=="":
                _util.MessageboxShowInfo("GPM", "The folder path is not set.")
                self.txt_output_clip.setFocus()
                return

            # 분리된 Tif 유역으로 자르기
            # gdalwarp -te -122.4267 37.7492 -122.4029 37.769 sf_4269.tif sf_4269-clippedByCoords.tif
            area =self.cmb_clip_zone.currentText()
            Clip_area=_Dict.Clip_dic[area]
            
            
#             for tif in (self.hdf_convert_tiff):
            if len(self.tb_clip_Tiff.selectedIndexes()) > 0: 
                #선택된 레이어에만 적용되도록...
                clip_pro_count=0;self.clip_progressBar.setMaximum(len(self.tb_clip_Tiff.selectedIndexes()))
                if os.path.exists(self.txt_output_clip.text()+"/"+str(area)+"/") == False:
                    folder = os.mkdir(self.txt_output_clip.text()+"/"+str(area)+"/")
                
                for idx in self.tb_clip_Tiff.selectedIndexes():
                    #HDF5 수행 후 바로라면.
                    if (self.hdf_convert_tiff != []):
                        tif = self.hdf_convert_tiff[idx.row()]
                        filename = _util.GetFilename(tif)
                        
                        Input = tif.replace(filename,filename+"_Convert")
                        Output = self.txt_output_clip.text()+"/"+str(area)+"/"+ filename + "_Clip.tif"
        # # #                 arg = "\"" + "C:/Program Files/GDAL/gdalwarp.exe" + "\""
        # # #                 arg = arg + " -te " + Clip_area + " \"" + Input + "\" " + "\"" + Output + "\" "
        # #                 # 좌표계 EPSG:4326 을 여기서 assign 해줌
                        try:
                            #우선 이 방식으로..
#                             osgeo4w="\"""C:/Program Files/QGIS 2.18/OSGeo4W.bat""\""
                            arg = "gdal_translate.exe -a_srs epsg:4326 -projwin  " +Clip_area + " -of GTiff "  +tif+ " " + Output
                            QgsMessageLog.logMessage(str(arg),"GPM CLIP")
#                             QgsMessageLog.logMessage(osgeo4w+" "+str(arg),"GPM CLIP")
        # #                 self.txt_output_clip.setText(arg)
        # #                 os.system(arg)
#                             sub.call(arg,shell=True)
#                             os.system(osgeo4w+" "+arg)
                            os.system(arg)
                            clip_pro_count =clip_pro_count+1
                            sleep(1)
                            self.clip_progressBar.setValue(clip_pro_count)
                        except Exception as e:
                            QgsMessageLog.logMessage(str(e),"GPM CLIP")
                
            else:
                _util.MessageboxShowInfo("GPM","Not Selected Files.")
        except Exception as e:
            _util.MessageboxShowInfo("GPM", str(e))
    
    
#     def clip_list(self, list):
#         list
    
    

#     # 좌표계 변환 -- old
#     def Convert_utm_tif(self,list):
#         try:
#             s_srs = _Dict.UTM_dic[str("WGS84_UTM 29N")]
#             t_srs=_Dict.UTM_dic[str("WGS84_UTM 29N")]
#             
#             cmd = "set GDAL_DATA=C:\Program Files\QGIS 2.18\share\gdal"
#             os.system(cmd)
#             
#             for file in list:
#                 filename = _util.GetFilename(file)      
#                 Output = file.replace(filename, filename + "_Convert")
#                 _util.ConvertUTM(file,Output,s_srs,t_srs) 
#             
#         except Exception as e:
#             _util.MessageboxShowError("GPM",str(e))


    # =============== UTM ===============================================
    def UTM_apply_Click(self):
        try:
            str_Input_folder = self.txt_input_utm.text()
            str_output_folder = self.txt_output_utm.text()
            if str_Input_folder.strip()=="":
                _util.MessageboxShowInfo("GPM","Select Directory")
                self.txt_input_utm.setFocus()
                return

#             if self.cmb_utm_source.currentIndex() == 0:
#                 _util.MessageboxShowInfo("GPM", "Not selected UTM")
#                 self.cmb_utm_source.setFocus()
#                 return
            
            if self.cmb_utm_target.currentIndex() == 0:
                _util.MessageboxShowInfo("GPM", "Not selected UTM")
                self.cmb_utm_target.setFocus()
                return

            if str_output_folder.strip()=="":
                _util.MessageboxShowInfo("GPM","Select Directory")
                self.txt_output_utm.setFocus()
                return
            
            UTM_Tiff_file_List=_util.GetFilelist(str_Input_folder,"tif")
            self.utm_progressBar.setValue(0)
            self.utm_progressBar.setMaximum(len(UTM_Tiff_file_List))
            
            # 좌표계 변환 실시
            self.Convert_utm(UTM_Tiff_file_List)
            
        except Exception as es:
            _util.MessageboxShowError("Error message", str(es))


    # 좌표계 변환
    def Convert_utm(self,list):
        os.environ['GDAL_DATA']='C:\Program Files\QGIS 2.18\share'
        
        try:
#             source=self.cmb_utm_source.currentText()
            target=self.cmb_utm_target.currentText()
#             s_srs = _Dict.UTM_dic[str(source)]
            t_srs=_Dict.UTM_dic[str(target)]

            utm_count=0
            for file in list:
                filename = _util.GetFilename(file)
                Output =self.txt_output_utm.text()+"/"+filename+"_UTM.tif" 
#                 
#                 file.replace(filename, filename + "_UTM")
#                 path ="‪C:/Program Files/GDAL/gdalwarp.exe"
#                 arg =path+ " -overwrite -s_srs "+ "\"" + s_srs +"\""+ " -t_srs "+"\"" + t_srs +"\"" + "-of GTiff "
# #                 gdalwarp.exe -s_srs " + " " + s_srs +" -t_srs " + " "+t_srs + " "
#                 arg = arg +" "+ file +" " + Output
                
                #gdalwarp.exe가 QGIS에도 있으므로... 굳이 경로 다 안써도 됨..;; _ JO                
                arg = 'gdalwarp.exe -overwrite -t_srs '+"\""+t_srs+"\""+(' -of GTiff {0} {1}').format(file,Output)
                exe=_util.Execute(arg)
                sleep(1)
                utm_count=utm_count+1
                self.utm_progressBar.setValue(utm_count)
                sleep(1)
                
#             _util.MessageboxShowInfo("GPM","Complete convert UTM.")
#                 _util.ConvertUTM(file,Output,s_srs,t_srs)
        except Exception as e:
            _util.MessageboxShowError("GPM",str(e))

    # =============== Resample===========================================
    def Resample_apply_Click(self):
        try:
            Input_folder = self.txt_input_resample.text()
            output_folder = self.txt_output_resample.text()
            cellvalue = str(self.cellsize.value())
            Method = self.cmb_resample_method.currentText()
            
            if Input_folder.strip() == "":
                _util.MessageboxShowInfo("GPM", "Select Directory")
                self.txt_input_resample.setFocus()
                return
            else:
                Resample_folder_list=_util.GetFilelist(Input_folder, "tif")

#             if self.cmb_resample_method.currentIndex() == 0:
#                 _util.MessageboxShowInfo("GPM", "Selected Method : None")
#                 self.cmb_resample_method.setFocus()
#                 return

            if output_folder.strip() == "":
                _util.MessageboxShowInfo("GPM", "Select Directory")
                self.txt_output_resample.setFocus()
                return
            
#             _util.MessageboxShowInfo("GPM Resample","Completed Resample")
#             _util.MessageboxShowError("test",str(len(Resample_folder_list)))
            try:
                self.resampling_progressBar.setValue(0)
                self.resampling_progressBar.setMaximum(len(Resample_folder_list))
                resample_count=0
                for file in Resample_folder_list:
                    filename = _util.GetFilename(file)
                    Output = output_folder + "/" +filename+"_resample.tif"
    #                 file.replace(filename,filename+"_resample")
                    _util.ExecuteGridResampling(Method,cellvalue,file,Output)
                    sleep(0.5)
                    resample_count=resample_count+1
                    self.resampling_progressBar.setValue(resample_count)
                    sleep(0.5)
            except Exception as e:
                _util.MessageboxShowError("GPM",str(e))    
        except Exception as ex:
            _util.MessageboxShowError("GPM",str(ex))


    # =============== ACCUM ===========================================
    def select_files(self):
        try: 
            self.tlb_filelist_Accum.clear() #초기화
            self.tlb_filelist_Accum.setRowCount(0)
            
            filter = "tif (*.tif)"
            file_name = QtGui.QFileDialog()
            file_name.setFileMode(QFileDialog.ExistingFiles)
            files = file_name.getOpenFileNamesAndFilter(self, "Open files", "C:\\", filter)
            FileList = files[0]

            self.tlb_filelist_Accum.setColumnCount(1)
            self.tlb_filelist_Accum.setHorizontalHeaderLabels(["Layer List"])
            stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
            self.tlb_filelist_Accum.setStyleSheet(stylesheet)
            
            count=0; self.accum_list = []
            for file in FileList:
                self.tlb_filelist_Accum.insertRow(count)
                self.tlb_filelist_Accum.setItem(count, 0, QTableWidgetItem(str(file)))
                self.accum_list.append(str(file))
                count = count + 1
                
            #프로그레스바 신설.. 내가 불편해서 만들었음
            self.acc_progressBar.setValue(0)
            self.acc_progressBar.setMaximum(len(self.accum_list))
                
        except Exception as e:
            _util.MessageboxShowInfo("GPM",str(e))
            
    #=====ACCUM APPLY=======
#     def AllCheck(self):
#         if self.chk_All_Check.setChecked(True):
#             self.chk_Accum_1H.setChecked(True)
#             self.chk_Accum_3H.setChecked(True)
#             self.chk_Accum_6H.setChecked(True)
#             self.chk_Accum_9H.setChecked(True)
#             self.chk_Accum_12H.setChecked(True)
#             self.chk_Accum_24H.setChecked(True)
#              
#         if self.chk_All_Check.setChecked(False):
#             self.chk_Accum_1H.setChecked(False)
#             self.chk_Accum_3H.setChecked(False)
#             self.chk_Accum_6H.setChecked(False)
#             self.chk_Accum_9H.setChecked(False)
#             self.chk_Accum_12H.setChecked(False)
#             self.chk_Accum_24H.setChecked(False)    
            

    
    def Accum_apply_Click(self):
        try:
            # OUTPUT 폴더
            accum_output = self.txt_output_accum.text()
            if accum_output.strip() =="":
                _util.MessageboxShowInfo("GPM", "The folder path is not set.")
                self.txt_output_accum.setFocus()
                return           
            
            #2018-10-26 필요없는 부분 제거
#             self.accum_rows=[];
#             if len(self.tlb_filelist_Accum.selectedIndexes())>0:
#                 for s_idx in self.tlb_filelist_Accum.selectedIndexes():
#                     self.accum_rows.append(s_idx.row())
#             else:
#                 _util.MessageboxShowError("GPM", "No columns selected or no layers.")
#                 return
#             QgsMessageLog.logMessage(str(band),"GPM ACCUM")
            
            #Accum 기능
            accum_run = self.Accum_Tiff()
            
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))
    
    def Accum_Tiff(self):
        #환경 설정 
        saga_ltr=os.environ["SAGA"] = 'C:/PROGRA~1/QGIS2~1.18/apps/saga-ltr'
        saga_modules=os.environ["SAGA_MLB"] ='C:/PROGRA~1/QGIS2~1.18/apps/saga-ltr/modules'
        PATH=os.environ["PATH"]='C:/PROGRA~1/QGIS2~1.18/apps/Python27/lib/site-packages/Shapely-1.2.18-py2.7-win-amd64.egg/shapely/DLLs;C:/PROGRA~1/QGIS2~1.18/apps/Python27/DLLs;C:/PROGRA~1/QGIS2~1.18/apps/Python27/lib/site-packages/numpy/core;C:/PROGRA~1/QGIS2~1.18/apps/qgis-ltr/bin;C:/PROGRA~1/QGIS2~1.18/apps/Python27/Scripts;C:/PROGRA~1/QGIS2~1.18/bin;C:/WINDOWS/system32;C:/WINDOWS;C:/WINDOWS/system32/WBem;C:/PROGRA~1/QGIS2~1.18/apps/saga-ltr;C:/PROGRA~1/QGIS2~1.18/apps/saga-ltr/modules'
        
        try:
#             self.accum_band_list = []
            self.Accum_Amount()
        except Exception as e:
            _util.MessageboxShowError("GPM Accum", str(e))
    
    def Accum_Amount(self):
        try:
            self.amount_list=[]
            #자꾸 꼬이는 것 같아서
            pro_count=0
            for filelist in self.accum_list:
                if os.path.exists(self.txt_output_accum.text()+"/Amount/") == False:
                    os.mkdir(self.txt_output_accum.text()+"/Amount/")
                    
                filename = _util.GetFilename(filelist)
                Output_Amount = self.txt_output_accum.text()+"/Amount/"+filename+"_Amount.tif"
                amount = _utilAC.accum_amount(filelist,Output_Amount)
                self.amount_list.append(str(Output_Amount))
                pro_count=pro_count+1
                self.acc_progressBar.setValue(pro_count/2)
                
            self.accum_check(self.amount_list)
            sleep(0.5)
            self.acc_progressBar.setValue(len(self.accum_list))
#             _util.MessageboxShowInfo("GPM", "Finish.")
#             for file2 in self.amount_list:   
#                 filename2 = _util.GetFilename(file2)
                #Accum
#                 Output_Accum = self.txt_output_accum.text() + "/"+filename2+"_Accum.tif"
#                 Output_Accum = filename2+"_Accum"
            # 아주 비효율 적이지만 목표는 되기만 하면 되거든
            
            
        except Exception as e:
            _util.MessageboxShowInfo("GPM Amount", str(e))
                
                
                
    def accum_check(self,list):
#         gdal_calc = os.path.dirname(os.path.abspath(__file__))+"/Lib/gdal_calc.py"
#         gdal_calc = "‪C:\Program Files\QGIS 2.18\bin\gdal_calc.py"
        
        try:
            #2018-10-17 JO : 라디오 버튼이 아닌 체크박스로 중복 수행 가능토록 변경
            if self.chk_Accum_1H.isChecked():
    #         if self.rdo_Accum_1H.isChecked():
                H1hour_list=[]
                if os.path.exists(self.txt_output_accum.text()+"/1H/") == False:
                    os.mkdir(self.txt_output_accum.text()+"/1H/")
                
                for f_accum in list:
                    filename=_util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text()+"/1H/"+filename+"_1H.tif"
                    H1hour_list.append(f_accum)
                    if len(H1hour_list) > 2:
                        del H1hour_list[1],H1hour_list[0]
                    if len(H1hour_list) == 2:
#                         QgsMessageLog.logMessage(str(H1hour_list),"GPM Accum Run 1H")
                        _utilAC.Accum_hour(H1hour_list,outputname)
                        
            #============ 3h ===========
            if self.chk_Accum_3H.isChecked():
                H3hour_list=[]
                if os.path.exists(self.txt_output_accum.text()+"/3H/") == False:
                    os.mkdir(self.txt_output_accum.text()+"/3H/")
                    
                for f_accum in list:
                    filename=_util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text()+"/3H/"+filename+"_3H.tif"    
                    H3hour_list.append(f_accum)
                    if len(H3hour_list) > 6:
                        del H3hour_list[5],H3hour_list[4],H3hour_list[3],H3hour_list[2],H3hour_list[1],H3hour_list[0]
                        
                    if len(H3hour_list) == 6:
#                         QgsMessageLog.logMessage(str(H3hour_list),"GPM Accum Run 3H")
                        _utilAC.Accum_hour(H3hour_list,outputname)
                    
#     #         if self.rdo_Accum_3H.isChecked():
#                 outputname = self.txt_output_accum.text()+"/3H/"+output+"_3H.tif"
#                 _utilAC.Accum_hour("3H",list,outputname)
#             
            #=============== 6H===================
            if self.chk_Accum_6H.isChecked():
                H6hour_list=[]
                if os.path.exists(self.txt_output_accum.text()+"/6H/") == False:
                    os.mkdir(self.txt_output_accum.text()+"/6H/")
                    
                for f_accum in list:
                    filename=_util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text()+"/6H/"+filename+"_6H.tif"    
                    H6hour_list.append(f_accum)
                    if len(H6hour_list) > 12:
                        del H6hour_list[11],H6hour_list[10],H6hour_list[9],H6hour_list[8],H6hour_list[7],
                        H6hour_list[6],H6hour_list[5],H6hour_list[4],H6hour_list[3],H6hour_list[2],H6hour_list[1],H6hour_list[0]
                        
                    if len(H6hour_list) == 12:
#                         QgsMessageLog.logMessage(str(H6hour_list),"GPM Accum Run 6H")
                        _utilAC.Accum_hour(H6hour_list,outputname)
                
            #=============== 9H===================
            if self.chk_Accum_9H.isChecked():
                H9hour_list=[]
                if os.path.exists(self.txt_output_accum.text()+"/9H/") == False:
                    os.mkdir(self.txt_output_accum.text()+"/9H/")
                    
                for f_accum in list:
                    filename=_util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text()+"/9H/"+filename+"_9H.tif"    
                    H9hour_list.append(f_accum)
                    if len(H9hour_list) > 18:
                        del H9hour_list[17],H9hour_list[16],H9hour_list[15],H9hour_list[14],H9hour_list[13],H9hour_list[12],
                        H9hour_list[11],H9hour_list[10],H9hour_list[9],H9hour_list[8],H9hour_list[7],H9hour_list[6],H9hour_list[5],
                        H9hour_list[4],H9hour_list[3],H9hour_list[2],H9hour_list[1],H9hour_list[0]
                    if len(H9hour_list) == 18:
#                         QgsMessageLog.logMessage(str(H9hour_list),"GPM Accum Run 9H")
                        _utilAC.Accum_hour(H9hour_list,outputname)
            #=============== 12H===================
            if self.chk_Accum_12H.isChecked():
                H12hour_list=[]
                if os.path.exists(self.txt_output_accum.text()+"/12H/") == False:
                    os.mkdir(self.txt_output_accum.text()+"/12H/")
                
                for f_accum in list:
                    filename=_util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text()+"/12H/"+filename+"_12H.tif"       
                
                    if len(H12hour_list) > 24:
                        H12hour_list.append(f_accum)
                        del H12hour_list[23],H12hour_list[22],H12hour_list[21],H12hour_list[20],H12hour_list[19],H12hour_list[18],H12hour_list[17],
                        H12hour_list[16],H12hour_list[15],H12hour_list[14],H12hour_list[13],H12hour_list[12],H12hour_list[11],H12hour_list[10],H12hour_list[9],H12hour_list[8],
                        H12hour_list[7],H12hour_list[6],H12hour_list[5],H12hour_list[4],H12hour_list[3],H12hour_list[2],H12hour_list[1],H12hour_list[0]
                    if len(H12hour_list) == 24:
                        _utilAC.Accum_hour(H12hour_list,outputname)
                    
            #=============== 24H===================
            if self.chk_Accum_24H.isChecked():
                H24hour_list=[]
                if os.path.exists(self.txt_output_accum.text()+"/24H/") == False:
                    os.mkdir(self.txt_output_accum.text()+"/24H/")
                for f_accum in list:
                    filename=_util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text()+"/24H/"+filename+"_24H.tif"   
                    
                    if len(H24hour_list)>48:
                        H24hour_list.append(f_accum)
                        del H24hour_list[47],H24hour_list[46],H24hour_list[45],H24hour_list[44],H24hour_list[43],H24hour_list[42],H24hour_list[41],H24hour_list[40],H24hour_list[39],
                        H24hour_list[38],H24hour_list[37],H24hour_list[36],H24hour_list[35],H24hour_list[34],H24hour_list[33],H24hour_list[32],H24hour_list[31],H24hour_list[30],H24hour_list[29],
                        H24hour_list[28],H24hour_list[27],H24hour_list[26],H24hour_list[25],H24hour_list[24],H24hour_list[23],H24hour_list[22],H24hour_list[21],H24hour_list[20],H24hour_list[19],
                        H24hour_list[18],H24hour_list[17],H24hour_list[16],H24hour_list[15],H24hour_list[14],H24hour_list[13],H24hour_list[12],H24hour_list[11],H24hour_list[10],H24hour_list[9],
                        H24hour_list[8],H24hour_list[7],H24hour_list[6],H24hour_list[5],H24hour_list[4],H24hour_list[3],H24hour_list[2],H24hour_list[1],H24hour_list[0]
                    if len(H24hour_list) == 48:
                        self.accum_band(H24hour_list, outputfile)
            
            
#     #         if self.rdo_Accum_6H.isChecked():
#                 
#                      
#                 outputname = self.txt_output_accum.text()+"/6H/"+output+"_6H.tif"
#                 _utilAC.Accum_hour("6H",list,outputname)
#              
#             if self.chk_Accum_9H.isChecked():
#     #         if self.rdo_Accum_9H.isChecked():
#                 if os.path.exists(self.txt_output_accum.text()+"/9H/") == False:
#                     folder = os.mkdir(self.txt_output_accum.text()+"/9H/")
#                 outputname = self.txt_output_accum.text()+"/9H/"+output+"_9H.tif"
#                 _utilAC.Accum_hour("9H",list,outputname)
#                  
#             
#     #         if self.rdo_Accum_12H.isChecked():
#                 if os.path.exists(self.txt_output_accum.text()+"/12H/") == False:
#                     folder = os.mkdir(self.txt_output_accum.text()+"/12H/")
#                 outputname = self.txt_output_accum.text()+"/12H/"+output+"_12H.tif"
#                 _utilAC.Accum_hour("12H",list,outputname)
#              
#             
#     #         if self.rdo_Accum_24H.isChecked():
#                 if os.path.exists(self.txt_output_accum.text()+"/24H/") == False:
#                     folder = os.mkdir(self.txt_output_accum.text()+"/24H/")
#                 outputname = self.txt_output_accum.text()+"/24H/"+output+"_24H.tif"
#                 _utilAC.Accum_hour("24H",list,outputname)
        except Exception as e:
            _util.MessageboxShowInfo("GPM ACCUM HOUR", str(e))

    # =============== MAKE CSV ===========================================
    def CSV_apply_Click(self):
        try:
            
            Input_file = self.txt_csv_shp.text()
            get_field = self.txt_fieldname_shp.text()
            output_file = self.txt_shp_field.text()
                        
            self.csv_file = open(output_file,'w+')
            self.csv_file.write("filename")
            if Input_file.strip() == "":
                _util.MessageboxShowInfo("GPM", "Select shp file ")
                self.txt_csv_shp.setFocus()
                return
            
            #나온 값을 csv 파일로 내보내면 됨.
            if output_file.strip() == "":
                _util.MessageboxShowInfo("GPM", "Select Save file name ")
                self.txt_shp_field.setFocus()
                return
            
            v_layer =QgsVectorLayer(Input_file,"SHP","ogr")
            
            if get_field.strip() =="":
                _util.MessageboxShowInfo("GPM", "The FieldName is not set.")
                self.txt_fieldname_shp.setFocus()
                return  
            
            try:
                self.get_shape_coord(v_layer,(self.txt_fieldname_shp.text()))
                
                cell_values = self.shape_coord_raster_cellvalue(self.filenames)
                _util.MessageboxShowInfo("Make CSV","Make CSV Function Completed.")
                
            except Exception as e:
                _util.MessageboxShowInfo("GPM", str(e))
#             field_name=self.get_shape_field(v_layer,self.txt_fieldname_shp.text())
            
            self.csv_file.close()
            
#             _util.ConvertShapeToCSV(Input_file,output_file)
        except Exception as e:
            _util.MessageboxShowError("GPM",str(e))
            
    
    #2018-10-19 : shape의 좌표, 필드 이름의 값 가져오기.
    def get_shape_coord(self,shapefile,txt):    
#         v_layer =QgsVectorLayer(shapefile,"SHP","ogr")
        
        prov = shapefile.dataProvider()
        features = shapefile.getFeatures()
        
        #필드 이름
        fieldNames = []
        fields = prov.fields()
        for field in fields:
#             QgsMessageLog.logMessage((str(field.name()).upper().decode('cp949').encode('utf-8')),"GPM CSV cp->utf8")
#             fieldNames.append( ((str(field.name())).upper()).decode('cp949').encode('utf-8') )
            fieldNames.append( ((str(field.name())).upper()))
#             QgsMessageLog.logMessage((str(field.name()).upper()),"GPM CSV ")
#             QgsMessageLog.logMessage((str(field.name()).upper().decode('utf-8').encode('utf-8')),"GPM CSV utf8->utf8")
#             QgsMessageLog.logMessage((str(field.name()).upper()).decode('utf-8','ignore'),"GPM CSV decode utf8->ignore")
#             QgsMessageLog.logMessage((str(field.name()).upper()).decode('cp949','utf-8'),"GPM CSV decode utf8->ignore")
#             QgsMessageLog.logMessage((str(field.name()).upper()).decode('euc-kr'),"GPM CSV decode 'euc-kr'")
#             QgsMessageLog.logMessage((str(field.name()).upper()).decode('euc-kr','cp949'),"GPM CSV decode 'euc-kr'->'cp949'")
#             QgsMessageLog.logMessage((str(field.name()).upper()).decode('euc-kr','ignore'),"GPM CSV decode 'euc-kr'->ignore")
#             QgsMessageLog.logMessage(unicode(str(field.name()).upper()),"GPM CSV unicode")
#             QgsMessageLog.logMessage((str(field.name()).upper()).decode('cp949','ignore'),"GPM CSV decode cp->ignore")
#             QgsMessageLog.logMessage((str(field.name()).upper()).encode('cp949'),"GPM CSV encode cp")
#             QgsMessageLog.logMessage((str(field.name()).upper()).decode('utf8'),"GPM CSV decode utf8")
#             QgsMessageLog.logMessage((str(field.name()).upper()).encode('utf8'),"GPM CSV encode utf8")
#             QgsMessageLog.logMessage(unicode(str(field.name()).upper(),'utf8'),"GPM CSV uni utf8")
            
            
            
#         for name in fieldNames:
#             if (name == txt):
#                 QgsMessageLog.logMessage(str(name),"GPM CSV 1")
#                 self.csv_file.write(str(name))
        self.point_list = []         
        #필드 값이 있는 것이면 수행. 없으면 msg
        if ((txt.upper())) not in fieldNames:
            _util.MessageboxShowInfo("GPM", "No have FieldName")       
        if ((txt.upper())) in fieldNames:
            for feat in features:
                #좌표값
                geom = feat.geometry()
                self.point_list.append(geom.asPoint())
#                 QgsMessageLog.logMessage(str((feat[(((txt.upper()).decode('cp949').encode('utf-8')))])),"GPM CSV")
                #필드 값
    #             QgsMessageLog.logMessage(str(feat[txt]),"GPM CSV 1")
#                 self.csv_file.write(","+str(feat[(((txt.upper()).decode('cp949').encode('utf-8')))]))
                self.csv_file.write(","+str(feat[(txt.upper())]))
            
                
    # shape 좌표 위치의 래스터 셀 값 가져오기
    # 래스터 선택해야 함.
    def shape_coord_raster_cellvalue(self,raster):
        try:
            for r_layer in raster:
                self.csv_file.write("\n"+r_layer)
                layer = QgsRasterLayer(r_layer)
                pixelWidth = layer.rasterUnitsPerPixelX()
                pixelHeight = layer.rasterUnitsPerPixelY()
                 
                for x, y in self.point_list:
                    ident = layer.dataProvider().identify(QgsPoint(x, y),QgsRaster.IdentifyFormatValue)
                    if ident.isValid():
    #                     QgsMessageLog.logMessage(str(ident.results()[1]),"GPM CSV 2")
                        self.csv_file.write(","+str(ident.results()[1]))
                
    #                     return str(ident.results()[1])
        except Exception as e:
            _util.MessageboxShowError("GPM",str(e))
   # =======================Funtion=======================================
    def select_files_func(self):
        try: 
            self.tlb_Function.clear() #초기화
            self.tlb_Function.setRowCount(0)
            
            filter = "tif (*.tif)"
            file_name = QtGui.QFileDialog()
            file_name.setFileMode(QFileDialog.ExistingFiles)
            files = file_name.getOpenFileNamesAndFilter(self, "Open files", "C:\\", filter)
            FileList = files[0]

            self.tlb_Function.setColumnCount(1)
            self.tlb_Function.setHorizontalHeaderLabels(["Layer List"])
            stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
            self.tlb_Function.setStyleSheet(stylesheet)
            
            
            count = 0;self.func_list = []
            for file in FileList:
                self.tlb_Function.insertRow(count)
                self.tlb_Function.setItem(count, 0, QTableWidgetItem(str(file)+"@1"))
                self.func_list.append(file)
                count=count+1
                
            # 테이블 데이터 수정 못하게 옵션
            self.tlb_Function.setEditTriggers(QTableWidget.NoEditTriggers)

        except Exception as e:
            _util.MessageboxShowInfo("GPM",str(e))
    
    
    def Fun_apply_Click(self):
        #아무래도 파일 불러오는 기능이 따로 있어야 하나 봅니다... 지금 제 눈에 이게 제일 쉬워보이니 이걸 먼저 해볼까요
        
        try:
            if "X".lower() in (self.txt_function_txt.text()):
                calculus = "("+(self.txt_function_txt.text()).replace("X".lower(), "X@1").replace("&", "and")+"*1)+0"
#                 calculus="("+self.txt_function_txt.text().replace("&", "and")+"*1)+0"
            path = self.txt_output_fun.text()
              
#             폴더 채택이 아닌 파일 단위로 결과 출력...
#             ☆★☆★ 2018-08-20 : 경로가 존재하지 않으면 오류 반환 ☆★☆★
            isPath=os.path.dirname(path)
            if os.path.isdir(isPath)==False:
                _util.MessageboxShowError("Morocco","This directory does not exist.")
                self.txt_output_fun.setFocus()
                return
               
            # 수식 칸이 빈칸이면 오류 반환
            if self.txt_function_txt.text().strip()=="":
                _util.MessageboxShowError("Morocco","The Operation you entered is incorrect or missing.")
                self.txt_function_txt.setFocus()
                return
            
            #여기서 선택한 레이어들만 식 적용되도록!
            select_list=[]
            for idx in self.tlb_Function.selectedIndexes():
                select_list.append(self.func_list[idx.row()])
            
#             for lyr in (self.func_list):
#                 ras = QgsRasterCalculatorEntry()
#                 ras.ref = "X@1"
#                 ras.raster = lyr
#                 ras.bandNumber = 1
#                 entries.append( ras )
#                 QgsMessageLog.logMessage(str(entries),"gpm func")
#                 if (lyr.name()) in select_list:
#                     ras.ref = lyr.name()+"@1"
                    
            entries = [] #참조된 레이어 리스트
            for lyr in _layers:
                ras = QgsRasterCalculatorEntry()
                if (lyr.name()) in select_list:
#                 ras.ref = lyr.name()+"@1"
                    ras.ref = "X@1"
                    ras.raster = lyr
                    ras.bandNumber = 1
                    entries.append( ras )
#        
#                     #calc = QgsRasterCalculator( '(ras@1 / ras@1) * ras@1', path + lyr.name() + "_suffix.tif", 'GTiff', lyr.extent(), lyr.width(), lyr.height(), entries )
                    calc = QgsRasterCalculator( calculus, path+"/"+lyr.name()+"_function.tif", 'GTiff', _layers[0].extent(), _layers[0].width(), _layers[0].height(), entries )
                    calc.processCalculation()
            _util.MessageboxShowInfo("GPM","Complete Raster Calculator.")
        except Exception as e:
            _util.MessageboxShowInfo("GPM",str(e))
       
    # table 셋팅
    def Set_table_list_fun(self):
        self.tlb_Function.setColumnCount(1)
        self.tlb_Function.setHorizontalHeaderLabels(["Layer List"])
        stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
        self.tlb_Function.setStyleSheet(stylesheet)

        count = 0 ; self.func_list=[]
        for layer in _layers:
            self.tlb_Function.insertRow(count)
            self.tlb_Function.setItem(count, 0, QTableWidgetItem(layer.name()+"@1"))
            self.func_list.append(layer.name())
            count=count+1

        # 테이블 데이터 수정 못하게 옵션
        self.tlb_Function.setEditTriggers(QTableWidget.NoEditTriggers)

        
    # 임시 기능 완료
    # =============== ASC ===============================================
    
    #======= ASC FILE SELECT ===========
    def select_ASC_files(self):
        dir = os.path.dirname(sys.argv[0])
        self.ASC_files = QFileDialog.getOpenFileNames(self,"Select Input FILES",dir,"GRM Project xml files (*.tif)",options=QtGui.QFileDialog.DontUseNativeDialog)
        self.txt_input_asc.setText(os.path.dirname(self.ASC_files[0]) +" || select count : "+ str(len(self.ASC_files)))
    
    #======= ASC APPLY=============
    def ASC_apply_Click(self):
        try:
            str_Input_file = self.ASC_files
            
            # 파일 선택이 안되어 있으면 다믐 메시지 반환
#             if str_Input_file.strip() == "":
            if len(str_Input_file) ==0:
                _util.MessageboxShowInfo("GPM", "Select Tif file ")
                self.txt_input_asc.setFocus()
                return
            
            # output 폴더 지정 안되어 있거나 폴더 경로가 올바르지 않을 경우 다음 메시지 반환
            if os.path.isdir(self.txt_output_asc.text())==False:
                _util.MessageboxShowError("GPM Make ASC","This directory does not exist.")
                self.txt_output_asc.setFocus()
                return
            
            i = 0 ; count_pro_asc=1; self.asc_progressBar.setValue(0); self.asc_progressBar.setMaximum(len(str_Input_file))
            for asc in str_Input_file:
                filename = _util.GetFilename(asc)
                output_filename = self.txt_output_asc.text() + ("/{0}.asc").format(filename)
                
#                 QgsMessageLog.logMessage(str(i) + " : "+ str(asc), "GPM CONVERT ASC")
#                 QgsMessageLog.logMessage(str(i) + " : "+ str(output_filename), "GPM CONVERT ASC")
#                 i=i+1
                _util.ConvertRasterToASC(asc,output_filename)
                sleep(1)
                self.asc_progressBar.setValue(count_pro_asc)
                count_pro_asc=count_pro_asc+1
                sleep(1)
#             self.txt_input_asc.text()
#             str_output_file = self.txt_output_asc.text()
#  

# 
        except Exception as e:
            _util.MessageboxShowError("Error message", str(e))
             

    # 트리 위젯에 메뉴 항목 설정
    def Set_treeWidget(self):
        self.treeWidget.setHeaderHidden(True)
        item9 = QtGui.QTreeWidgetItem(self.treeWidget, ['Data Download'])
        icon = QtGui.QIcon(settings_icon)
        item9.setIcon(0, icon)
        
        item = QtGui.QTreeWidgetItem(self.treeWidget, ['HDF5_Convert'])
        icon = QtGui.QIcon(settings_icon)
        item.setIcon(0, icon)
        item0 = QtGui.QTreeWidgetItem(self.treeWidget, ['Clip'])
        icon = QtGui.QIcon(settings_icon)
        item0.setIcon(0, icon)
        item1 = QtGui.QTreeWidgetItem(self.treeWidget, ['UTM'])
        icon = QtGui.QIcon(settings_icon)
        item1.setIcon(0, icon)
        item2 = QtGui.QTreeWidgetItem(self.treeWidget, ['Resampling'])
        icon = QtGui.QIcon(settings_icon)
        item2.setIcon(0, icon)
        item3 = QtGui.QTreeWidgetItem(self.treeWidget, ['Accum'])
        icon = QtGui.QIcon(settings_icon)
        item3.setIcon(0, icon)
        item4 = QtGui.QTreeWidgetItem(self.treeWidget, ['Make CSV'])
        icon = QtGui.QIcon(settings_icon)
        item4.setIcon(0, icon)
        item5 = QtGui.QTreeWidgetItem(self.treeWidget, ['Function'])
        icon = QtGui.QIcon(settings_icon)
        item5.setIcon(0, icon)
        item6 = QtGui.QTreeWidgetItem(self.treeWidget, ['Make ASC'])
        icon = QtGui.QIcon(settings_icon)
        item6.setIcon(0, icon)
        item7 = QtGui.QTreeWidgetItem(self.treeWidget, ['Satellitecorrection'])
        icon = QtGui.QIcon(settings_icon)
        item7.setIcon(0, icon)
        item8 = QtGui.QTreeWidgetItem(self.treeWidget, ['Make Image'])
        icon = QtGui.QIcon(settings_icon)
        item8.setIcon(0, icon)
        
        

        self.mainLayout = QtGui.QGridLayout(self)
        self.mainLayout.addWidget(self.treeWidget)
        self.treeWidget.itemDoubleClicked.connect(self.OnDoubleClick)

    # 메뉴 트리 목록에서 아이템 클릭했을때 이벤트 처리
    def OnDoubleClick(self, item):
        try:
            SelectItme = item.text(0)
            if SelectItme == 'HDF5_Convert':
                self.tabWidget.setCurrentIndex(1)
            if SelectItme == 'Clip':
                self.tabWidget.setCurrentIndex(2)
            elif SelectItme == "UTM":
                self.tabWidget.setCurrentIndex(3)
            elif SelectItme == "Resampling":
                self.tabWidget.setCurrentIndex(4)
            elif SelectItme == "Accum":
                self.tabWidget.setCurrentIndex(5)
            elif SelectItme == 'Make CSV':
                self.tabWidget.setCurrentIndex(6)
            elif SelectItme == 'Function':
                self.tabWidget.setCurrentIndex(7)
            elif SelectItme == 'Make ASC':
                self.tabWidget.setCurrentIndex(8)
            elif SelectItme == 'Satellitecorrection':
                self.tabWidget.setCurrentIndex(9)
            elif SelectItme == 'Make Image':
                self.tabWidget.setCurrentIndex(10)
            elif SelectItme == 'Data Download':
                self.tabWidget.setCurrentIndex(0)

        except Exception as es:
            _util.MessageboxShowError("Error message", str(es))


        #--------------------------------연대 모듈 연동 --------------------------------------------------------
#     def Save_gif_path(self):
#         filename = QFileDialog.getSaveFileName(self, "select output file ", "", "*.gif")
#         if len(filename)>0:
#             self.txt_gif_Path.setText(filename)

    # 테이블 헤더 설정
    def SetTable_header(self):
        self.lisw_ASC.setColumnCount(1)
        self.lisw_ASC.setRowCount(0)
        self.lisw_ASC.setHorizontalHeaderLabels(["ASC"])

        self.lisw_Convert_file.setColumnCount(1)
        self.lisw_Convert_file.setRowCount(0)
        self.lisw_Convert_file.setHorizontalHeaderLabels(["CSV"])

    def MoveUp(self,table):
        row = table.currentRow()
        column = table.currentColumn()
        if row > 0:
            table.insertRow(row - 1)
            for i in range(table.columnCount()):
                table.setItem(row - 1, i, table.takeItem(row + 1, i))
                table.setCurrentCell(row - 1, column)
            table.removeRow(row + 1)


    def MoveDown(self,table):
        row = table.currentRow()
        column = table.currentColumn()
        if row >= 0:
            if row < table.rowCount() - 1:
                table.insertRow(row + 2)
                for i in range(table.columnCount()):
                    table.setItem(row + 2, i, table.takeItem(row, i))
                    table.setCurrentCell(row + 2, column)
                table.removeRow(row)

    def ReMove(self,table):
        row = table.currentIndex().row()
        mess="Are you sure you want to delete the selected items?"
        result=QMessageBox.question(None, "Watershed Setup",mess,QMessageBox.Yes, QMessageBox.No)
        if result == QMessageBox.Yes:
            table.removeRow(row)
#             2018-09-10 JO : 목록에 표시만 제거될 뿐 내부적으로 적용 안됨.
            

    #버튼 아이콘 
    def set_btn_icon(self):
        #btn_Apply 버튼의 아이콘 넣기
        btn_apply_icon = os.path.dirname(os.path.abspath(__file__))+"/icon/bottom_arrow.png"
        self.btn_Apply.setIcon(QtGui.QIcon(btn_apply_icon))

    # 레이어 목록 혹은 파일 목록사용여부 라디오버튼
    def Select_radio_event(self):
        if self.rdo_Layer.isChecked():
            self.txt_Input_data.setDisabled(True)
            self.btnOpenDialog_Input.setDisabled(True)
            # QGIS 레이어 목록을 리스트 박스에 셋팅 하기
            self.Set_Listbox()
        else:
            self.txt_Input_data.setDisabled(False)
            self.btnOpenDialog_Input.setDisabled(False)


    # Qgis Layer 목록 리스트 뷰에 넣기
    def Set_Listbox(self):
        global _ASC_filename
        #del _ASC_filename[:]
        self.lisw_ASC.setRowCount(0)
        for row in (_ASC_filename):
            counts = self.lisw_ASC.rowCount()
            self.lisw_ASC.insertRow(counts)
            self.lisw_ASC.setItem(counts, 0, QTableWidgetItem(row))

    #사용자가 ASC 파일경로를 다이얼 로그로 받아 오는 부분
    def Select_ASC_event(self):
        # 2018-05-08:수정
        # 리스트 초기화
        self.lisw_ASC.setRowCount(0)
        global _ASC_filename
        del _ASC_filename[:]

        dir = os.path.dirname(sys.argv[0])
        try:
            # 사용자가 선택한 파일 목록
            _ASC_filename = QFileDialog.getOpenFileNames(self,"Select Input ASC FILES",dir,"*.asc *.ASC ",options=QtGui.QFileDialog.DontUseNativeDialog)
            
            #btnOpenDialog_Input에 선택한 파일들의 폴더 경로 넣기
            self.txt_Input_data.setText(os.path.dirname(_ASC_filename[0]))
            
            # 선택된 파일들을 리스트 박스에 넣기
            for row in (_ASC_filename):
                counts = self.lisw_ASC.rowCount()
                self.lisw_ASC.insertRow(counts)
                self.lisw_ASC.setItem(counts, 0, QTableWidgetItem(row))
            _util.MessageboxShowInfo("Satellite", str(len(_ASC_filename))+" FILES SELECTED")
        except Exception as e:
            _util.MessageboxShowError("Satellite", " A file selection error occurred. ")
            return

    # CSV 선택파일 다이얼로그
    def Select_CSV_event(self):
        # 기본 경로
        dir = os.path.dirname(sys.argv[0])
        global select_file#,select_file_path
        
        try:
            # 파일은 하나만 선택하게 함.
#             select_file = QFileDialog.getOpenFileName(self, "Select csv file.", dir, '*.csv *.CSV',options=QtGui.QFileDialog.DontUseNativeDialog)
            #기존 2017버전으로 복귀
            select_file = QFileDialog.getOpenFileNames(self, "Select csv files.", dir, '*.csv *.CSV',options=QtGui.QFileDialog.DontUseNativeDialog)
#             select_file_path = os.path.dirname(select_file[0])
            
            # 선택한 csv 파일의 폴더경로를 받음
            self.txt_Convert_path.setText(str(os.path.dirname(select_file[0])))
            self.list_set_csv()
            
            
            
            
        except Exception as e:
            # 파일 선택 창을 그냥 닫는 경우
            self.txt_Convert_path.setText("")
            return
    
    #csv 원상복귀(2017 버전으로)
    def list_set_csv(self):
        self.lisw_Convert_file.setRowCount(0)
        try:
            for row in (select_file):
                counts = self.lisw_Convert_file.rowCount()
                self.lisw_Convert_file.insertRow(counts)
                self.lisw_Convert_file.setItem(counts, 0, QTableWidgetItem(row))
        except Exception as e:
            _util.MessageboxShowError("GPM",str(e))
        
    
    # CSV 파일 변환 이벤트
    def Convert_CSV_event(self):
        #lisw_Convert_file 리스트 초기화
        self.lisw_Convert_file.setRowCount(0)
        opencsv = open(select_file, 'r')
        reader_csv = csv.reader(opencsv)
        '''
        #5/11 참고참고::
                    뭐랄까 코드가 이동하면서 한글이 깨지는 것 같음... 문제가 되는 부분이 있다면 좌표값으로 변환할 때 매우 크게 문제가 되고 있어용.. 전부 1,1 이렇게 되니까..
        '''
        # 헤더 지역 받아옴
        headercsv = opencsv.readline().decode('cp949').encode('utf-8')
        # 헤더 지역별로 배열생성
        AreaName = headercsv.split(',')
        AreaCoord = []
        for i in AreaName[1:]:
            print
            #AreaCoord.append(self.coordinate_dict(i))
            '''
            5/21 jo :
            #마지막 값이 1,1 로 출력되는 오류 찾음
            #원인은 위치 마지막 키 값에 \n 이 들어 있어서 except 문을 타고 1,1로 출력된 것.
            #해당 문제가 없도록 replace를 사용해서 해당 오류 해결하였음.
            '''
            AreaCoord.append(_coord.coordinate_dict(i.replace("\n","")))
        i = 1
        #self.CSV_filepath = []#여기에 썼더니 값은 2개 들어오는데 리스트엔 3개가 뜨는 매직..!?
        global _CSV_filename
        del _CSV_filename[:]
        for row in (reader_csv):
            #2018-10-26 이 부분에서 오작동이 있던 것인데 파일 명만 받도록 변경하였음.
            #포맷이 주신 샘플로 고정이 되어야 함. 아니면 다시 오류 발생 가능성이 아주 높음
            getfile = _util.GetFilename(str(row[0]))
            # 파일 생성 코드..
            # 위치는 선택한 csv 파일과 같은 경로에 생성됨
            create_csv = open(select_file_path + "/{0}.csv".format(getfile), 'w+')
            # 흠 리스트로 받아서 처리 하려 했건만 잘안됨 나중에 확인..하나씩만 들어오는..
            self.CSV_filepath = []
            self.CSV_filepath.append(select_file_path + "/{0}.csv".format(getfile))
            # 2018 -06-11 기능 다시 넣음 (쪼.....)
            counts = self.lisw_Convert_file.rowCount()
            self.lisw_Convert_file.insertRow(counts)
            self.lisw_Convert_file.setItem(counts, 0, QTableWidgetItem(select_file_path + "/{0}.csv".format(getfile)))
            global _CSV_filename
            _CSV_filename.append(select_file_path + "/{0}.csv".format(getfile))
            
            j = 0
            for cols in row[i:]:
                value = AreaCoord[j] + "," + cols + "\n"
                j += 1
                create_csv.write(value)
                
        
        create_csv.close()
        opencsv.close()
        # 변환완료되었음을 알림
        _util.MessageboxShowInfo("Info", "Complete convert file")
        # txt_Convert_path 텍스트 값 초기화
        self.txt_Convert_path.clear()
    #    self.closewindow()

    
    #기존의 기능으로 원복(이름으로 매칭... 일단 이 방법)
    def Apply_all_correction(self):
        if len(_ASC_filename) != len(select_file):
            QgsMessageLog.logMessage("Number of CSV FILES and ASC FILES do not match.","GPM NOTICE")
            return
        try:
            self.decimalChanged()
            run_correction = _corr.run_correction(output_folder, _ASC_filename, select_file, _decimal)
            for count in range(len(select_file)):
                if self.chk_AddLayer.isChecked():
                    self.Addlayer_OutputFile(
                        output_folder + "\\" + (os.path.basename(_ASC_filename[count]).split(".")[0]) + "_" + (
                            os.path.basename(select_file[count]).split(".")[0]) + ".asc")
                count = count + 1
            
            #그럼 여기서 새로 리스트 만들어서 넣음..
            self.Tree_Result.clear()
            self.Tree_Result.setHeaderLabels(["Apply List"])
            i=0
            for ASC in range(len(_ASC_filename)):
                root = QtGui.QTreeWidgetItem(self.Tree_Result,[_ASC_filename[ASC]])
                value = _ASC_filename[i]
                SS = QtGui.QTreeWidgetItem(root,[value])
                if self.chk_makePng.isChecked():
                    SS = QtGui.QTreeWidgetItem(root, [value.replace("asc","png")])
                    _PNG_filename.append(value.replace("asc","png"))
                    png_path=value.replace("asc","png")
                    # 이미지 생성
                    self.make_png(_ASC_filename[ASC],png_path)
                i=i+1

        except Exception as es:
            QMessageBox.information(None, "error", str(es))
        
        
        
        
    
    # 모든 리스트가 적용 되었을때 파일 목록으로 정
    def Apply_AllList_event(self):
        global _decimal,_PNG_filename
        # CSV 파일과 ASC 파일의 갯수가 같지 않으면 오류 메시지 출력
        if len(_CSV_filename)!= len(_ASC_filename):
            QgsMessageLog.logMessage("Number of CSV FILES and ASC FILES do not match.","GPM NOTICE")
            return
        try:
            self.decimalChanged()
            run_correction = _corr.run_correction(output_folder, _ASC_filename, _CSV_filename, _decimal)
            for count in range(len(_CSV_filename)):
                if self.chk_AddLayer.isChecked():
                    self.Addlayer_OutputFile(
                        output_folder + "\\" + (os.path.basename(_ASC_filename[count]).split(".")[0]) + "_" + (
                            os.path.basename(_CSV_filename[count]).split(".")[0]) + ".asc")
                count = count + 1
#             _util.MessageboxShowInfo("Process Information","performed {0} files. \n{1}".format(len(_ASC_filename), str(run_correction)))

#             # 진행률 바가 100%가 되면 자동으로 메세지 바 삭제
#             GPM._iface.messageBar().clearWidgets()

            #그럼 여기서 새로 리스트 만들어서 넣음..
            self.Tree_Result.clear()
            self.Tree_Result.setHeaderLabels(["Apply List"])
            i=0
            for ASC in range(len(_ASC_filename)):
                root = QtGui.QTreeWidgetItem(self.Tree_Result,[_ASC_filename[ASC]])
                value = _CSV_filename[i]
                SS = QtGui.QTreeWidgetItem(root,[value])
                if self.chk_makePng.isChecked():
                    SS = QtGui.QTreeWidgetItem(root, [value.replace("csv","png")])
                    _PNG_filename.append(value.replace("csv","png"))
                    png_path=value.replace("csv","png")
                    # 이미지 생성
                    self.make_png(_ASC_filename[ASC],png_path)
                i=i+1

        except Exception as es:
            QMessageBox.information(None, "error", str(es))


    #폼 화면 종료(닫기)
    def Close_Form(self):
        self.close()

    def decimalChanged(self):
        global _decimal
        _decimal = self.decimalBox.value()

    # 레이어 목록 Qgis에 올리기
    def Addlayer_OutputFile(self, outputpath):
        if (os.path.isfile(outputpath)):
            fileName = outputpath
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            GPM._iface.addRasterLayer(fileName, baseName)

    #output 경로 받기
    def Output_path_Dialog(self):
         global output_folder
         output_folder=""
         #output_path = select_file_path
         output_path = os.path.dirname(sys.argv[0])
         #asc 선택과 달리 폴더 지정
         output_folder =(QFileDialog.getExistingDirectory(self,"Select Output Directory",output_path))
         
         #선택 폴더가 있다면
         if output_folder !="":
            self.txtOutputDataPath.setText(output_folder)
         #선택 폴더가 없다면
         else:
             self.txtOutputDataPath.setText("")

    #ok 버튼 누르면 실행 되는 부분임
    def run_Result(self):
        global _decimal
        count=0
        save_path = output_folder

        progress = QProgressBar()#progress bar 공통 부분1
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)#progress bar 공통 부분2

        self.decimalChanged()
#         start_time = time.time()
        run_correction=_corr.run_correction(save_path,_ASC_filename,(self.CSV_filename),_decimal)

        #종료시간
#         print ("--- %s seconds ---" %(time.time() - start_time))

        for count in range(len(self.CSV_filename)):
            if self.chk_AddLayer.isChecked() :
                self.Addlayer_OutputFile(save_path+"\\"+(os.path.basename(_ASC_filename[count]).split(".")[0])+"_"+(os.path.basename(self.CSV_filename[count]).split(".")[0])+".asc")

            count= count +1
            #진행률 바 생성
            progressMessageBar = GPM._iface.messageBar().createMessage(("Progress rate"))
            progressMessageBar.layout().addWidget(progress)
            GPM._iface.messageBar().pushWidget(progressMessageBar, GPM._iface.messageBar().SUCCESS)
            progress.setMaximum(len(_ASC_filename))
             
            #진행률 % 표현
            progress.setValue(count)
 
        _util.MessageboxShowInfo("Process Information","performed {0} files. \n{1}".format(len(_ASC_filename),str(run_correction)))

        #진행률 바가 100%가 되면 자동으로 메세지 바 삭제
        GPM._iface.messageBar().clearWidgets()

    def make_png(self, asc_path, png_path):
        color_path = os.path.dirname(os.path.realpath(__file__)) + "/Color/color.txt"
#         arg = "gdaldem.exe color-relief " + asc_path + " " + color_path + " " + png_path
        # v0.0.14 수정해보았음.
        mycall =[osgeo4w,
                 "gdaldem.exe",
                 "color-relief",
                 asc_path,
                 color_path,
                 png_path]
        callvalue = sub.call(mycall,shell=True)
#         QgsMessageLog.logMessage(str(callvalue),"GPM PNG")
#         returnValue = _util.Execute(arg)
#         if returnValue != 0:
        if callvalue != 0:
            _util.MessageboxShowInfo("Notice", "Not completed.")

#     def make_gif(self):
#         try:
#             # 이미지 목록 리스트
#             img_list = []
#             if len(_PNG_filename)>0:
#                 for file in (_PNG_filename):
#                     img_list.append(imageio.imread(file))
#                 imageio.mimsave(self.txt_gif_Path.text(), img_list, duration=(self.Interval_box.value()))
#             else:
#                 _util.MessageboxShowError("Notice","No PNG file selected.")
#             QMessageBox.information(None, "Notice", "Make GIF")
#         except Exception as ex:
#             QMessageBox.Warning(None, "Notice", str(ex))


    #===========Make image ============
    
    def Folder_List(self,type):
        try:
             folderpath  =QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', '', QtGui.QFileDialog.ShowDirsOnly)
             filelsit=self.search(folderpath)
             self.SettingListWidget(filelsit,type)
        except Exception as e:
            _util.MessageboxShowError("GPM",str(e))
    
    
    def SettingListWidget(self,filelsit,type):

        if type=="ASC":
            self.tbl_asc_list.clear()
            for file in filelsit:
                filename = os.path.splitext(file)[1]
                if ".ASC" in filename.upper() :
                    self.tbl_asc_list.addItem(file)

        else:
            self.btl_png_list.clear()
            for file in filelsit:
                filename = os.path.splitext(file)[1]
                if ".PNG" in filename.upper() :
                    self.btl_png_list.addItem(file)

    def search(self,dirname):
        fileList=[]
        if dirname!="" and dirname is not None:
            filenames = os.listdir(dirname)
            for filename in filenames:
                filePath = os.path.join(dirname, filename)
                fileList.append(filePath)
        return fileList


    #사용자가 ASC 파일이 포함된 폴더를 선택하고 직접 PNG 파일로 변환 하는 함수
    def Make_png_menu(self):
        try:
            self.btl_png_list.clear() #수행시 초기화 v0.0.14 추가
            items = self.tbl_asc_list.selectedItems()
            if len(items)>0:
                for i in list(items):
                    #2018-10-25 v0.0.14 추가
                    asc_file = _util.GetFilename(i.text())
                    png_name = self.txt_output_png.text() + "/"+asc_file.upper()+".PNG"
                    sleep(0.5)
                    self.make_png(i.text(), png_name)
                    sleep(0.5)
                    self.btl_png_list.addItem(png_name)
#                     self.btl_png_list.addItem(i.text().upper().replace(".ASC",".PNG"))
                    #self.Png_Add_Text(i.text().upper().replace(".ASC",".PNG"))
            else:
                _util.MessageboxShowError("GPM","No ASC file selected.")
                return
        except Exception as e:
            _util.MessageboxShowError("GPM",str(e))

    def Make_gif_user(self):
        try:
            if self.txt_save_gif_path_imag.text()=="":
                _util.MessageboxShowError("GPM","The file path is not set.")
                self.txt_save_gif_path_imag.setFocus()
                return

            # 이미지 목록 리스트
            img_list = []
            items = self.btl_png_list.selectedItems()
            if len(items)>0:
                for file in (items):
                    self.Png_Add_Text(str(file.text()))
                    sleep(0.5)
                    img_list.append(imageio.imread(file.text()))
                    
                sleep(1)
                imageio.mimsave(self.txt_save_gif_path_imag.text(), img_list, duration=(self.Interval_box_imag.value()))
                
                
            else:
                _util.MessageboxShowError("Notice","No PNG file selected.")
                return
            QMessageBox.information(None, "Notice", "Make GIF")
        except Exception as ex:
            QMessageBox.Warning(None, "Notice", str(ex))

    def Png_Add_Text(self,filepath):
        try:
            #img = Image.open("C:/Users/hermesys/Desktop/Convert/2.png")
            #draw = ImageDraw.Draw(img)
            #font = ImageFont.truetype("sans-serif.ttf", 20)
            #draw.text((0, 0),"test",(255,255,255),font=font)
            #img.save("C:/Users/hermesys/Desktop/Convert/2.png")


            
            # 글자 사이즈 값은 나중에 조절 해야 할듯함
            im1=Image.open(filepath)
            width, height = im1.size
            #2018-10-26 요청에 따라 크기 줄임
            font_size=int(width/30)
#             QgsMessageLog.logMessage(str(font_size)+" : "+str(height)+" : "+str(width),"GPM IMG")
            font = ImageFont.truetype("./arial.ttf", font_size)
            fileName=_util.GetFilename(filepath)
#             QgsMessageLog.logMessage(fileName.split("_")[0],"GPM IMG")
            # Drawing the text on the picture
            draw = ImageDraw.Draw(im1)
#             draw.text((0, 0),fileName,(255,0,128),font=font)
#             draw.text((0, 0),(fileName.split("_")[0]),(255,0,128),font=font)
            file_name_replace = str((fileName.split("_")[0]).split("-")[0:]).replace(", ","-").replace("'","")
            print file_name_replace
            draw.text((0, 0),file_name_replace,(255,255,0),font=font)
            draw = ImageDraw.Draw(im1)
 
            # Save the image with a new name
            im1.save(filepath)
        except Exception as e:
            _util.MessageboxShowInfo("GPM", str(e))

    
    
    
    
    # ================== wget data download ===============
    def wget_save_path(self):
        global wget_folder
        wget_path = os.path.dirname(sys.argv[0])
        wget_folder =(QFileDialog.getExistingDirectory(self,"Select Output Directory",wget_path))
        self.txt_bat_path.setText(wget_folder)
        
        
    def wget_create_bat(self):
        try:
            wget.create_bat_script(self.start_date.text(),self.end_date.text(),wget_folder)
            _util.MessageboxShowInfo("GPM", "A batch file was created on the desktop.")
#             _util.MessageboxShowInfo("GPM", ("바탕화면에 GPM_data_download.bat 파일이 생성되었습니다.").decode('utf-8'))
        except Exception as e:
            _util.MessageboxShowError("GPM",str(e))
    

    
    
#===================================================20180531 추가
#     #이미지 선택... PNG 이미지(n 개) 선택하는 창
#     def img_path(self):
#         global FilePaths
#
#         #기본 경로
#         dir = os.path.dirname(sys.argv[0])
#
#         #btn_selectImgs 버튼 클릭 시 사용자가 PNG 파일 (n 개) 선택할 수 있는 다이얼로그 창이 뜸
#         FilePaths = QFileDialog.getOpenFileNames(self,"Select image files.",dir,"*.png *.PNG",options=QtGui.QFileDialog.DontUseNativeDialog)
#         #혹시 폴더만 선택해서 폴더에 png를 찾는 방식인 경우엔 폴더 선택은 아래와 같음
# #         FilePaths=(QFileDialog.getExistingDirectory(self,"Select Directory",dir))
#         #폴더 선택의 경우 파일에서 PNG만 찾는 소스도 필요함.여기엔 없음.
#
#
#
#         #선택한 파일 목록 리스트를 텍스트 박스(txt_imgPath)에 나타냄
#         self.txt_imgPath.setText(str(FilePaths))
#
#
#     #선택한 PNG 파일 목록을 받아서 1 GIF 생성하는 함수
#     def img2gif(self):
#
#         #임시..
#         #GIF 생성 시 파일 구분 용으로 날짜_시간이 파일 명 뒤에 붙도록 하였음
#         # now = time.localtime()
#         # date_time = "%04d%02d%02d_%02d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
#
#         # #결과파일은 선택한 파일과 같은 경로로 날짜와시간을 표시해서 출력(리스트 중 첫번째 파일명을 사용)
#         # output_gif = "{0}/{1}_{2}.gif".format(os.path.dirname(FilePaths[0]),
#         #                                        os.path.splitext(os.path.basename(FilePaths[0]))[0],
#         #                                        date_time)
#         #
#         try:
#             #이미지 목록 리스트
#             img_list = []
#             for file in _PNG_filename:
#                 img_list.append(imageio.imread(file))
#
#             #입력받은 이미지를 GIF 파일로 저장
#             #duration을 조정함으 GIF 의 속도를 조절할 수 있음 현재 기본 셋팅은 0.5로 해두었음.
#             #출력 결과, 입력받은 이미지, GIF 속도
#             imageio.mimsave(self.txt_gif_Path.text(), img_list, duration=(self.Interval_box.value()))
#
#             #수행 완료 시...
#             QMessageBox.information(None,"Notice","Make GIF")
#         except Exception as ex:
#             QMessageBox.information(None,"Notice",str(ex))
#

#===================================================

