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

import os, sys, shutil
# bin_directory ="C:/Program Files/QGIS 2.18/apps/qgis-ltr/python/qgis;"
# os.environ['PATH'] += os.path.pathsep + bin_directory

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
import Dict_Clip as dCilp
import GPM
import csv
# from PyQt4.QtGui import QFileDialog

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/Lib')
import imageio
import OneFileCorrection_class as OneFile
import coordinate_class
import util_accum
from time import  sleep
import time
import ProgressBar
import wget
import transpose_Tiff as tr_Tiff
# import shlex
import Canvas_Tools

_iface = {}
# 2018-08-06 박: 기능 테스트로 임시 추가 
# function 기능으로 추가 테스트중
import qgis
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from PyQt4.QtGui import QProgressDialog, QProgressBar
from osgeo import *
# from Scripts.gdal_calc import Calc

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GPM_dialog_base.ui'))

path = os.path.dirname(os.path.realpath(__file__))
settings_icon = path + '\image\settings.png'
_util = util.util()
_layers = {}
_Dict = Dict.dict()
_Dict_clip = dCilp.dict_clip()

_coord = coordinate_class.place_to_coordinate()
_corr = OneFile.satellite_correction()
_utilAC = util_accum.accum_util()

'''
2018-09-09 JO:
csv 파일 변환하는 함수에서 _coord 로 해둔 부분이 있음.
해당 부분은 장소 명을 좌표로 바꾸는 부분임.
옮겨쓰는 과정에서 지워졌나봄. 상단에  import만 되어 있음.
2018-06 버전에서는 해당 부분이 있음.
'''
_coord = coordinate_class.place_to_coordinate()
_corr = OneFile.satellite_correction()
_utilAC = util_accum.accum_util()
_tr_Tiff = tr_Tiff.transpose_Tiff_class()

os.environ['GDAL_DATA'] = os.popen('gdal-config --datadir').read().rstrip()
bin_directory = r"c://Program Files/QGIS 2.18/OSGeo4W.bat"
os.environ['PATH'] += os.path.pathsep + bin_directory
osgeo4w = "c://Program Files/QGIS 2.18/OSGeo4W.bat"

cursor = 0

_ASC_filename = []
# _CSV_filename=[]
# select_file=[]
select_file = ""
_PNG_filename = []
# fieldNames=[]
# convert_crs=[]

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
        _ASC_filename = _util.Qgis_Layer_list(layers)

        # 2018-06-11 박: 테이블 헤더 기본 셋팅
        self.SetTable_header()
        # 2018 -05-08 : 프로그램 수정
        # 라디오 버튼 기본 설정

        self.rdo_Layer.setChecked(True)

        self.rdo_Layer.toggled.connect(self.Select_radio_event)

        self.rdo_Files.toggled.connect(self.Select_radio_event)

        self.Select_radio_event()
        
        # 2018-10-31츄가
        # 사용자가 참조할 SHP 파일 선택 이벤트.
        self.btn_inputSHP.clicked.connect(self.input_Ref_SHP)
        
        # 사용자가 ASC 파일 선택 이벤트
        self.btnOpenDialog_Input.clicked.connect(self.Select_ASC_event)

        # CSV 파일 선택 이벤트
        self.btn_Select_Covert_File.clicked.connect(self.Select_CSV_event)

        # Convert 버튼 이벤트
#         self.btn_Covert.clicked.connect(self.Convert_CSV_event)
        self.btn_Covert.clicked.connect(self.Convert_CSV_time)

        # btn_Apply 버튼 이벤트 모든 리스트 파일이 있을때 작동
#         self.btn_Apply.clicked.connect(self.Apply_AllList_event)
        self.btn_Apply.clicked.connect(self.Apply_all_correction)

        # decimal 숫자 초기화(항상 0부터 시작하도록, 초기화)
        self.decimalBox.setValue(0)
        
        # 프로그램 종료
        # self.btnClose.clicked.connect(self.Close_Form)
        
        # 버튼 아이콘 설정
        self.set_btn_icon()

        # 사용자가 output 다이얼로그를 눌렀을 때 이벤트 처리
        self.btnOutputDialog.clicked.connect(self.Output_path_Dialog)

        # OK 버튼 누르면 Satellite correction이 수행됨
        # self.btnOK.clicked.connect(self.run_Result)

        # Result load to canvas 버튼 기본 체크 상태
        self.chk_AddLayer.setChecked(True)
        # Make PNG 체크박스는 기본 체크 상태
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
#         self.btn_csvRemove.clicked.connect(lambda: self.ReMove(self.lisw_Convert_file,self._CSV_filename))

        self.btn_ASCup.clicked.connect(lambda : self.MoveUp(self.lisw_ASC))
        self.btn_ASCdown.clicked.connect(lambda: self.MoveDown(self.lisw_ASC))
        self.btn_ASCremove.clicked.connect(lambda: self.ReMove(self.lisw_ASC))
#         self.btn_ASCremove.clicked.connect(lambda: self.ReMove(self.lisw_ASC,_ASC_filename))

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
        
        # wget_data download
#         self.userOS=""
        self.rdo_64.setChecked(True)  # 2019-03-13 필리핀 교육에서 32bit os가 등장해서 개발버전에서만 추가함.
        self.rdo_64.clicked.connect(self.Rdo_Selected_wget)
        self.rdo_32.clicked.connect(self.Rdo_Selected_wget)
        self.btn_bat_path.clicked.connect(self.wget_save_path)
        self.btn_datadownload.clicked.connect(self.wget_create_bat)

        # png_canvas, Canvas 추가함.
        _canvas = Canvas_Tools.Canvas_Tools(self.gpm_canvas)
#         self.base_shp()
        self.shp_layer_point = ""
        self.shp_layer_line = ""
        self.shp_layer_polygon = ""
        self.btn_pngshp_polygon.clicked.connect(self.btn_baseShp_polygon)  # polygon(유역도)
        self.btn_pngshp_line.clicked.connect(self.btn_baseShp_line)  # Line(하천망도)
        self.btn_pngshp_point.clicked.connect(self.btn_baseShp_point)  # Point(관측소 위치)
        
        # 클립 영역 선택 콤보 박스 셋팅 (한반도 , 남한 영역, 필리핀, 모로코 영역)
        # self.cmb_clip_zone.addItems(["Select Country","Korea","South_Korea","Philippines","Morocco", "Korea_Typoon"])
        self.cmb_clip_zone.addItems(_Dict_clip.cmb_Clip)
#         self.cmb_utm_source.addItems(["Select UTM","WGS84_UTM 28N","WGS84_UTM 29N","WGS84_UTM 30N","WGS84_UTM 50N","WGS84_UTM 51N","WGS84_UTM 52N","WGS84_UTM 53N"])
        self.cmb_utm_target.addItems(["Select UTM",
                                      'WGS84_UTM 1N', 'WGS84_UTM 1S', 'WGS84_UTM 2N', 'WGS84_UTM 2S', 'WGS84_UTM 3N', 'WGS84_UTM 3S', 'WGS84_UTM 4N', 'WGS84_UTM 4S', 'WGS84_UTM 5N', 'WGS84_UTM 5S',
                                      'WGS84_UTM 6N', 'WGS84_UTM 6S', 'WGS84_UTM 7N', 'WGS84_UTM 7S', 'WGS84_UTM 8N', 'WGS84_UTM 8S', 'WGS84_UTM 9N', 'WGS84_UTM 9S', 'WGS84_UTM 10S', 'WGS84_UTM 11N',
                                      'WGS84_UTM 11S', 'WGS84_UTM 12N', 'WGS84_UTM 12S', 'WGS84_UTM 13N', 'WGS84_UTM 13S', 'WGS84_UTM 14N', 'WGS84_UTM 14S', 'WGS84_UTM 15N', 'WGS84_UTM 15S', 'WGS84_UTM 16N', 'WGS84_UTM 16S',
                                      'WGS84_UTM 17N', 'WGS84_UTM 17S', 'WGS84_UTM 18N', 'WGS84_UTM 18S', 'WGS84_UTM 19N', 'WGS84_UTM 19S', 'WGS84_UTM 20N', 'WGS84_UTM 20S', 'WGS84_UTM 21N', 'WGS84_UTM 21S', 'WGS84_UTM 22N',
                                      'WGS84_UTM 22S', 'WGS84_UTM 23N', 'WGS84_UTM 23S', 'WGS84_UTM 24N', 'WGS84_UTM 24S', 'WGS84_UTM 25N', 'WGS84_UTM 25S', 'WGS84_UTM 26N', 'WGS84_UTM 26S', 'WGS84_UTM 27N', 'WGS84_UTM 27S',
                                      'WGS84_UTM 28N', 'WGS84_UTM 28S', 'WGS84_UTM 29N', 'WGS84_UTM 29S', 'WGS84_UTM 30N', 'WGS84_UTM 30S', 'WGS84_UTM 31N', 'WGS84_UTM 31S', 'WGS84_UTM 32N', 'WGS84_UTM 32S', 'WGS84_UTM 33N',
                                      'WGS84_UTM 33S', 'WGS84_UTM 34N', 'WGS84_UTM 34S', 'WGS84_UTM 35N', 'WGS84_UTM 35S', 'WGS84_UTM 36N', 'WGS84_UTM 36S', 'WGS84_UTM 37N', 'WGS84_UTM 37S', 'WGS84_UTM 38N', 'WGS84_UTM 38S',
                                      'WGS84_UTM 39N', 'WGS84_UTM 39S', 'WGS84_UTM 40N', 'WGS84_UTM 40S', 'WGS84_UTM 41N', 'WGS84_UTM 41S', 'WGS84_UTM 42N', 'WGS84_UTM 42S', 'WGS84_UTM 43N', 'WGS84_UTM 43S', 'WGS84_UTM 44N',
                                      'WGS84_UTM 44S', 'WGS84_UTM 45N', 'WGS84_UTM 45S', 'WGS84_UTM 46N', 'WGS84_UTM 46S', 'WGS84_UTM 47N', 'WGS84_UTM 47S', 'WGS84_UTM 48N', 'WGS84_UTM 48S', 'WGS84_UTM 49N', 'WGS84_UTM 49S',
                                      'WGS84_UTM 50N', 'WGS84_UTM 50S', 'WGS84_UTM 51N', 'WGS84_UTM 51S', 'WGS84_UTM 52N', 'WGS84_UTM 52S', 'WGS84_UTM 53N', 'WGS84_UTM 53S', 'WGS84_UTM 54N', 'WGS84_UTM 54S', 'WGS84_UTM 55N',
                                      'WGS84_UTM 55S', 'WGS84_UTM 56N', 'WGS84_UTM 56S', 'WGS84_UTM 57N', 'WGS84_UTM 57S', 'WGS84_UTM 58N', 'WGS84_UTM 58S', 'WGS84_UTM 59N', 'WGS84_UTM 59S', 'WGS84_UTM 60N', 'WGS84_UTM 60S'])
        
#         self.cmb_resample_method.addItems(["Select Method","near","bilinear","cubic","cubicspline","lanczos","average","mode","max","min","med","q1","q3"])
        self.cmb_resample_method.addItems(["bilinear", "near", "cubic", "cubicspline", "lanczos", "average", "mode", "max", "min", "med", "q1", "q3"])
        
        # 라디오 버튼 초기화
        self.rdo_Combo_Clip.setChecked(True)
        self.Rdo_Selected()

        # 라디오 버튼 이벤트 처리
        self.rdo_Combo_Clip.clicked.connect(self.Rdo_Selected)
        self.rdo_Shape_Clip.clicked.connect(self.Rdo_Selected)
        self.rdo_user_clip.clicked.connect(self.Rdo_Selected)

        # Shape 파일 경로 받아 오기
        self.btn_shape_dialog.clicked.connect(lambda :self.Shape_Select(self.txt_Shape_path))

        # 폴더 선택 다이얼로그
        self.btn_Output_Folder.clicked.connect(lambda :self.Select_Folder_Dialog(self.txt_output_clip))

        #2018-09-03=================
        # convert Apply 버튼 클릭 인벤트
        # 김주훈 박사님과 협의 사항으로 기능을 병합 하기로함
        
        #2018-10-15 추가 ========
        self.btn_input_hdf5.clicked.connect(self.select_hdf5)
        self.txt_hdf5_inPath.setText("Grid")
        self.txt_hdf_inName.setText("precipitationCal")
        # 2018-10-15 End
        
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
        # self.btn_input_accum.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_input_accum))

        self.btn_output_accum.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_output_accum))
        # self.btn_shp_accum.clicked.connect(lambda: self.Save_File_Dialog(self.txt_reference_shp,"shp"))
        
        self.btn_apply_accum.clicked.connect(self.Accum_apply_Click)
        
        # convert CSV
#         self.txt_fieldname_shp.setText("u_id")
#         self.btn_csv_shp.clicked.connect(lambda: self.Shape_Select(self.txt_csv_shp))
        self.btn_csv_shp.clicked.connect(self.read_SHP)
        self.btn_csv_csv.clicked.connect(lambda: self.Save_File_Dialog(self.txt_shp_field, "csv"))
#         (lambda: self.Save_File_Dialog(self.txt_shp_field,"shp"))
        self.btn_raster_tiff.clicked.connect(self.raster_tiff_select)
        self.btn_apply_CSV.clicked.connect(self.CSV_apply_Click)
         
        # function 
        self.btn_input_function.clicked.connect(self.select_files_func)
        self.btn_apply_Function.clicked.connect(self.Fun_apply_Click)
        # 테이블 데이터 셋팅
#         self.Set_table_list_fun()
         
        # Make ASC
        self.txt_input_asc.setEnabled(False)  # only 버튼을 클릭하여 파일 선택할 수 있음
        self.btn_input_asc.clicked.connect(self.select_ASC_files)
#             lambda: self.Select_File_Dialog(self.txt_input_asc))
        self.btn_output_asc.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_output_asc))
#             lambda: self.Save_File_Dialog(self.txt_output_asc,"asc"))
        self.btn_apply_ASC.clicked.connect(self.ASC_apply_Click)
        
        # Make image
        self.chk_polygon.stateChanged.connect(self.chk_selected)
        self.chk_line.stateChanged.connect(self.chk_selected)
        self.chk_point.stateChanged.connect(self.chk_selected)
#         self.chk_selected() #shp 사용 여부 선택
        self.btn_output_png.clicked.connect(lambda :self.Select_Folder_Dialog(self.txt_output_png))
        
    # ★★★★★★★★★★★★★★★★★★★★★★★  2018-08-20 ★★★★★★★★★★★★★★★★★★★
#         self.tlb_Function.doubleClicked.connect(self.double_click)
#         self.txt_function_txt.cursorPositionChanged.connect(self.txtFuntion)
#         self.btn_input_Function.clicked.connect(lambda:self.saveFileDialog("TIF"))
        self.txt_function_txt.setText("x+1")
        self.btn_input_Function.clicked.connect(lambda: self.Select_Folder_Dialog(self.txt_output_fun))  # 폴더 선택으로 변경
    
    # 저장 경로 입력 받기 
    def saveFileDialog(self, type):
        if type.upper() == "TIF":
            file = str(QFileDialog.getSaveFileName(self, "Save Folder Path", "C://", ".tif"))
            self.txt_output_fun.setText(file)
        else:
            file = str(QFileDialog.getSaveFileName(self, "Save GIF Path", "C://", ".gif"))
            self.txt_save_gif_path_imag.setText(file)
    
    # txt_function_txt에서 현재 커서의 위치를 반환하기
    def txtFuntion(self):
        global cursor
        cursor = self.txt_function_txt.cursorPosition()

    # 더블 클릭시 txt_function_txt에 클릭한 레이어 이름을 커서 위치에 삽입
    def double_click(self):
        try:
            row = self.tlb_Function.currentRow()
            item = self.tlb_Function.item(row, 0).text()
            
            self.txt_function_txt.setText(self.txt_function_txt.text()[:cursor] + "\"" + item + "\"" + self.txt_function_txt.text()[cursor:])
            
        except Exception as e:
            _util.MessageboxShowError("Flood", str(e))
    
    # ★★★★★★★★★★★★★★★ ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    # ===============Convert==============================================
    def Set_Convert_table_layerlist(self):
        self.tb_hdf5.setColumnCount(1)
        self.tb_hdf5.setHorizontalHeaderLabels(["Layer List"])

        stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
        self.tb_hdf5.setStyleSheet(stylesheet)
        count = 0
        # 레이어 데이터 경로 받아서 배열에 미리 넣어 두기
        self.layer_Data = []
        self.layer_Name = []
        # 2018-10-15 잠시 보류
#         for layer in _layers:
#             self.tb_hdf5.insertRow(count)
#             self.tb_hdf5.setItem(count, 0, QTableWidgetItem(layer.name()))
#             self.layer_Data.append(str(layer.dataProvider().dataSourceUri()))
#             self.layer_Name.append(layer.name())
#             count = count+1

    # =============== Clip ===============================================
    # 테이블에 레이어 목록을 셋팅 하기
    def Set_Clip_table_layerlist(self):
        self.tb_clip_Tiff.clear()  # 초기화
        self.tb_clip_Tiff.setRowCount(0)
        
        self.tb_clip_Tiff.setColumnCount(1)
        self.tb_clip_Tiff.setHorizontalHeaderLabels(["Layer List"])
        stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
        self.tb_clip_Tiff.setStyleSheet(stylesheet)
        count = 0
        
        # 불편해서 프로그레스바 추가함. 힘들다
        self.clip_progressBar.setValue(0)
        
        for layer in (self.hdf_convert_tiff):
            self.tb_clip_Tiff.insertRow(count)
#             self.tb_clip_Tiff.setItem(count, 0, QTableWidgetItem(layer.name()))
            self.tb_clip_Tiff.setItem(count, 0, QTableWidgetItem(layer))
            count = count + 1
        
        # 2018-10-15 잠시 보류
#         for layer in _layers:
#             self.tb_clip_Tiff.insertRow(count)
#             self.tb_clip_Tiff.setItem(count, 0, QTableWidgetItem(layer.name()))
#             count=count+1
         # 테이블 데이터 수정 못하게 옵션
        self.tb_clip_Tiff.setEditTriggers(QTableWidget.NoEditTriggers)
    
    # check box 선택 여부
    def chk_selected(self):
#         if self.chk_polygon.checkState() == 0:
#             QgsMessageLog.logMessage(str(self.chk_polygon.checkState()),"GPM IMG")
#             self.btn_pngshp_polygon.setEnabled(False)
# #         if self.chk_polygon.checkState() == 1:
# #             self.btn_pngshp_polygon.setEnabled(True)
        if self.chk_polygon.isChecked():
            self.btn_pngshp_polygon.setEnabled(True)
        else:
            self.btn_pngshp_polygon.setEnabled(False)
            
        if self.chk_line.isChecked():
            self.btn_pngshp_line.setEnabled(True)
        else:
            self.btn_pngshp_line.setEnabled(False)
        
        if self.chk_point.isChecked():
            self.btn_pngshp_point.setEnabled(True)
        else:
            self.btn_pngshp_point.setEnabled(False)
    
    def Rdo_Selected(self):
        if self.rdo_Combo_Clip.isChecked():
            self.cmb_clip_zone.setEnabled(True)
#             self.txt_Shape_path.setEnabled(False)
            self.btn_shape_dialog.setEnabled(False)
            self.clip_1_x.setEnabled(False)
            self.clip_1_y.setEnabled(False)
            self.clip_2_x.setEnabled(False)
            self.clip_2_y.setEnabled(False)
            
        elif self.rdo_Shape_Clip.isChecked():
            self.cmb_clip_zone.setEnabled(False)
            # self.txt_Shape_path.setEnabled(True)
            self.btn_shape_dialog.setEnabled(True)
            self.clip_1_x.setEnabled(False)
            self.clip_1_y.setEnabled(False)
            self.clip_2_x.setEnabled(False)
            self.clip_2_y.setEnabled(False)
            
        else:
            self.clip_1_x.setEnabled(True)
            self.clip_1_y.setEnabled(True)
            self.clip_2_x.setEnabled(True)
            self.clip_2_y.setEnabled(True)
            self.cmb_clip_zone.setEnabled(False)
            self.btn_shape_dialog.setEnabled(False)

    def Shape_Select(self, txt):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'c://', "Shape files (*.shp)")
        if _util.CheckFile(fname):
            txt.setText(fname)

    def Select_Folder_Dialog(self, txt):
        Folder = str(QFileDialog.getExistingDirectory(self, "Select Directory", 'c://'))
        if _util.CheckKorea(Folder):
            _util.MessageboxShowInfo("GPM","Check Path, No used Korean.\nPlease use English.")
        
        if _util.CheckFolder(Folder):
            txt.setText(Folder)

    # 파일 선택 다이얼 로그 나중에 Util 파일로 변경해야함
    def Select_File_Dialog(self, txt):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'select output file', '', 'GRM Project xml files (*.tif)', options=QtGui.QFileDialog.DontUseNativeDialog)
        txt.setText(filename)

    def  Save_File_Dialog(self, txt, type):
        try:
            if type == "asc":
                filename = QtGui.QFileDialog.getSaveFileName(self, 'save file', 'c://', filter="asc (*.asc *.)")
                txt.setText(filename)
            elif type == "shp":
                filename = QtGui.QFileDialog.getSaveFileName(self, 'save file', 'c://', filter="shp (*.shp *.)")
                txt.setText(filename)
            elif type == "csv":
                filename = QtGui.QFileDialog.getSaveFileName(self, 'save file', 'c://', filter="csv (*.csv *.)")
                txt.setText(filename)
        except Exception as se:
            _util.MessageboxShowInfo("GPM", str(se))
    
    def raster_tiff_select(self):
        self.filenames = QFileDialog.getOpenFileNames(self, 'Open file', 'c://', 'GRM Project xml files (*.tif)')
        self.txt_raster_tiff.setText(str(self.filenames))
#         QFileDialog.getOpenFileNames(self,"Select Input ASC FILES",dir,"*.asc *.ASC ",options=QtGui.QFileDialog.DontUseNativeDialog)

    #============HDF5TOTIFF APPLY================
    def select_hdf5(self):
        try:
            self.tb_hdf5.clear()  # 초기화
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
            count = 0
            
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
            if foldersss.strip() == "":
                _util.MessageboxShowInfo("GPM", "The folder path is not set.")
                self.txt_Output_Convert.setFocus()
                return
            
            # 2018-10-15 : 리스트에서 선택 X 파일 선택 단계에서 이미 선택한 것으로 가정
#             self.rows = []
#             if len(self.tb_hdf5.selectedIndexes()) > 0:
#                 for idx in self.tb_hdf5.selectedIndexes():
#                     self.rows.append(idx.row())
#             else:
#                 _util.MessageboxShowError("GPM", "No columns selected or no layers.")
#                 return

            # 사용자가 원하는 파일을 tiff 파일로 분리 함수
            Tiff_List = self.BandtoTiff()
            # 결과 좌표계 설정 
            self.Convert_crs_tif(self.MaketoTif)
            
#             self.Convert_utm_tif(self.MaketoTif)
            
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))
            
    # tiff 분리 하기
    def BandtoTiff(self):
        try:
            self.MaketoTif = []
            for idx in self.hdf5_list:
#             for idx in self.tb_hdf5.selectedIndexes():
                datasouce = idx
#                 self.hdf5_list[idx.row()]
#                 QgsMessageLog.logMessage(str(datasouce),"GPM TIFF")
                name = _util.GetFilename(datasouce)
                # 변환된 원본 TIFF 저장 폴더 생성
                folder = self.txt_Output_Convert.text() + "/step1/"
                if os.path.exists(folder) == False:
                    os.mkdir(folder)
#                 name = self.hdf5_list[idx.row()].replace(":","_").replace("/","").replace("\"","").strip()
                self.MaketoTif.append(folder + name + "_precipitationCal.tif")
# #                 arg = "gdal_translate.exe "  + "\"" + datasouce + "\"" + " -of GTiff "  +  "\"" + self.txt_Output_Convert.text() + "\\" + name + ".tif" + "\""
                
                output = folder + name + "_" + self.txt_hdf_inName.text() + ".tif"
#                 QgsMessageLog.logMessage(str(output),"GPM TIFF output")
                try:
#                     arg = "gdal_translate.exe HDF5:" + "\"" + str(datasouce) + "\"" + "://{0}/{1} -of GTiff {2}".format(self.txt_hdf5_inPath.text(), self.txt_hdf_inName.text(), output)
                    arg ='gdal_translate.exe HDF5:"{0}"://{1}/{2} -of GTiff "{3}"'.format(str(datasouce),self.txt_hdf5_inPath.text(),self.txt_hdf_inName.text(),output)
                    sub.call(arg, shell=True)
#                     os.system(arg)
#                     QgsMessageLog.logMessage(str(arg),"GPM TIFF")
#                     arg=[
#                         osgeo4w,"gdal_translate.exe",
#                         "HDF5:",str(datasouce),"://",
#                         str(self.txt_hdf5_inPath.text()),
#                         "/",str(self.txt_hdf_inName.text()),
#                         "-of","GTiff",str(output)
#                     ]
#                     QgsMessageLog.logMessage(str(arg),"GPM TIFF")
#                     sub.call(arg) #,shell=True) #2019-02-25, 전면 수정
#                 arg = "gdal_translate.exe HDF5:"+ "\"" + str(datasouce) +"\""+"://{0}/{1} -of GTiff {2}/{3}".format(self.txt_hdf5_inPath.text(),self.txt_hdf_inName.text(),self.txt_Output_Convert.text(),name+"_"+self.txt_hdf_inName.text()+".tif" )
#                     QgsMessageLog.logMessage(str(arg),"GPM TIFF")
#                 exe=_util.Execute(arg)
#                 arg = "gdal_translate.exe HDF5:"+ "\"" + str(datasouce) +"\""+"://{0}/{1} -of GTiff {2}/{3}".format(self.txt_hdf5_inPath.text(),self.txt_hdf_inName.text(),self.txt_Output_Convert.text(),name+"_"+self.txt_hdf_inName.text()+".tif" )
#                     QgsMessageLog.logMessage(str(arg),"GPM TIFF")
#                 exe=_util.Execute(arg)
                    
#                     os.system(arg)
#                     run_arg=[osgeo4w,
#                           "gdal_translate","HDF5",
#                           "\"",str(datasouce),"\"",
#                           "://",self.txt_hdf5_inPath.text(),
#                           "/",self.txt_hdf_inName.text(),
#                           "-of","GTiff",output]
                    subprocess.call(arg, shell=True)  # 도스 창 안 뜨게해주세요 요청
                    # 결과 파일이 안 만들어지면 중간에 끝내 버리도록 해버림.(어차피 없으면 진행 안됨)
                    if os.path.exists(output) == True:
                        pass
                    elif os.path.exists(output) != True:
                        _util.MessageboxShowError("GPM", "Failed Create output file.")
                        self.hdf5_progressBar.setValue(0)
                        return
                    
                except Exception as e:
                    QgsMessageLog.logMessage(str(e), "GPM TIFF")
                    
            self.hdf5_progressBar.setValue(0)    
            self.hdf5_progressBar.setMaximum(len(self.MaketoTif))
            
        except Exception as e:
            _util.MessageboxShowError("Error message", str(e))
    
    # made in JO - 좌표계 변환... - 20180913
    def Convert_crs_tif(self, list):
        try:
            
            try:
                self.hdf_convert_tiff = [] ; hdf_pro_count = 0
                for file in list:
                    # 가로세로 변환된 원본 TIFF 저장 폴더 생성
                    folder = self.txt_Output_Convert.text() + "/step2/"
                    if os.path.exists(folder) == False:
                        os.mkdir(folder)
                        
                    filename = _util.GetFilename(file)
#                     output = folder+name+"_"+self.txt_hdf_inName.text()+".tif"
                    Output = folder + filename + "_Convert.tif"
#                     QgsMessageLog.logMessage(str(Output),"GPM HDF5")
#                     Output = file.replace(filename, filename + "_Convert")
                    
                    # 2018-11-15 numpy 사용으로 변경
                    # transpose_TIFF =  _tr_Tiff.img_to_array(file,Output)
    #                2018-09-16 JO : 원exe2 사용
                    converter_exe = os.path.dirname(os.path.abspath(__file__)) + "/Lib/kict_sra_gpm_converter\KICT_SRA_GPM_Converter.exe" 
                    call_convert = sub.call([converter_exe, file, Output], shell=True)
                    # 정상적으로 수행이 된 경우 0, 이 경우 파일을 삭제
                    if call_convert == 0 :
                        os.remove(file)
                    
                    # 2018-10-17 : JO - output 파일이 실존하면 리스트에 추가되도록 수정함. 
                    try:
                        if (os.path.exists(Output)) == True:
                            self.hdf_convert_tiff.append(Output)
                            hdf_pro_count = hdf_pro_count + 1
                            self.hdf5_progressBar.setValue(hdf_pro_count)
                            sleep(1)
                            
                        elif (os.path.exists(Output)) != True:
                        # 맵윈도우가 없으면 실행이 안되니까...
                            _util.MessageboxShowInfo("GPM", "Please check Manual(Part install Mapwindow5).")
                    except Exception as e:
                        _util.MessageboxShowInfo("GPM", str(e))
                        
            except Exception as e:
                _util.MessageboxShowInfo("GPM", str(e))
            
            if call_convert == 0 :
                    # step1 폴더 삭제...
                os.rmdir(os.path.dirname(file))
#             self.calc((len(self.hdf_convert_tiff)*1000), (len(self.hdf_convert_tiff)*2000))
#             self.calc(len(self.hdf_convert_tiff)*5)
            # clip 준비... 2018-10-15 신설
            self.Set_Clip_table_layerlist()
        except Exception as e:
            _util.MessageboxShowError("GPM" , str(e))

    #========CLIP APPLY=========
    # clip 파일 지정
    def select_Cilp_files(self):
        try: 
            self.tb_clip_Tiff.clear()  # 초기화
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
            count = 0
            
            self.hdf_convert_tiff = []
            for file in FileList:
                self.tb_clip_Tiff.insertRow(count)
                self.tb_clip_Tiff.setItem(count, 0, QTableWidgetItem(str(file)))
                self.hdf_convert_tiff.append(str(file))
                
#                 count+=1
                count = count + 1
            # 프로그레스바 신설.. 내가 불편해서 만들었음
            self.acc_progressBar.setValue(0)
                
        except Exception as e:
            _util.MessageboxShowInfo("GPM", str(e))
    
    # clip apply
    def Clip_apply_Click(self):
        os.environ['GDAL_DATA'] = 'C:\Program Files\QGIS 2.18\share'
        try:
            # clip zone comboBox 지정 여부 확인
            if self.rdo_Combo_Clip.isChecked():
                if self.cmb_clip_zone.currentIndex() == 0 :
                    _util.MessageboxShowInfo("GPM" , "Not selected Country")
                    self.cmb_clip_zone.setFocus()
                    return
            elif self.rdo_Shape_Clip.isChecked():
                Path_txt = self.txt_Shape_path.text()
                if Path_txt.strip() == "":
                    _util.MessageboxShowInfo("GPM", "The file path is not set.")
                    self.txt_Shape_path.setFocus()
                    return
            
            # 결과 파일 출력 경로 지정 여부 확인
            foldersss = self.txt_output_clip.text()
            if foldersss.strip() == "":
                _util.MessageboxShowInfo("GPM", "The folder path is not set.")
                self.txt_output_clip.setFocus()
                return
            
            if self.rdo_Combo_Clip.isChecked():
                self.cmb_clip_zone_apply()
#                 self.txt_output_clip.clear() #경로 초기화....
                            
            elif self.rdo_Shape_Clip.isChecked():
                self.Shape_Clip_apply()
#                 self.txt_output_clip.clear() #경로 초기화....
            
            elif self.rdo_user_clip.isChecked():
                self.user_Clip_apply()
            
            # 분리된 Tif 유역으로 자르기
            # gdalwarp -te -122.4267 37.7492 -122.4029 37.769 sf_4269.tif sf_4269-clippedByCoords.tif
#             area =self.cmb_clip_zone.currentText()
#             Clip_area=_Dict.Clip_dic[area]
            
#             for tif in (self.hdf_convert_tiff):
#             if len(self.tb_clip_Tiff.selectedIndexes()) > 0: 
#                 #선택된 레이어에만 적용되도록...
#                 clip_pro_count=0;self.clip_progressBar.setMaximum(len(self.tb_clip_Tiff.selectedIndexes()))
#                 if os.path.exists(self.txt_output_clip.text()+"/"+str(area)+"/") == False:
#                     folder = os.mkdir(self.txt_output_clip.text()+"/"+str(area)+"/")
#                 
#                 for idx in self.tb_clip_Tiff.selectedIndexes():
#                     #HDF5 수행 후 바로라면.
#                     if (self.hdf_convert_tiff != []):
#                         tif = self.hdf_convert_tiff[idx.row()]
#                         filename = _util.GetFilename(tif)
#                         
#                         Input = tif.replace(filename,filename+"_Convert")
#                         Output = self.txt_output_clip.text()+"/"+str(area)+"/"+ filename + "_Clip.tif"
#         # # #                 arg = "\"" + "C:/Program Files/GDAL/gdalwarp.exe" + "\""
#         # # #                 arg = arg + " -te " + Clip_area + " \"" + Input + "\" " + "\"" + Output + "\" "
#         # #                 # 좌표계 EPSG:4326 을 여기서 assign 해줌
#                         try:
#                             #우선 이 방식으로..
# #                             osgeo4w="\"""C:/Program Files/QGIS 2.18/OSGeo4W.bat""\""
#                             arg = "gdal_translate.exe -a_srs epsg:4326 -projwin  " +Clip_area + " -of GTiff "  +tif+ " " + Output
#                             QgsMessageLog.logMessage(str(arg),"GPM CLIP")
# #                             QgsMessageLog.logMessage(osgeo4w+" "+str(arg),"GPM CLIP")
#         # #                 self.txt_output_clip.setText(arg)
#         # #                 os.system(arg)
# #                             sub.call(arg,shell=True)
# #                             os.system(osgeo4w+" "+arg)
#                             os.system(arg)
#                             clip_pro_count =clip_pro_count+1
#                             sleep(1)
#                             self.clip_progressBar.setValue(clip_pro_count)
#                         except Exception as e:
#                             QgsMessageLog.logMessage(str(e),"GPM CLIP")
#                 
#             else:
#                 _util.MessageboxShowInfo("GPM","Not Selected Files.")
        except Exception as e:
            _util.MessageboxShowInfo("GPM", str(e))

    # ===== 여기가 combo area 선택 함수 생성
    def cmb_clip_zone_apply(self):
        # 분리된 Tif 유역으로 자르기
            # gdalwarp -te -122.4267 37.7492 -122.4029 37.769 sf_4269.tif sf_4269-clippedByCoords.tif
            area = self.cmb_clip_zone.currentText()
#             Clip_area=_Dict.Clip_dic[area]
            Clip_area = _Dict_clip.Clip_dic[area]
#             for tif in (self.hdf_convert_tiff):
            if len(self.tb_clip_Tiff.selectedIndexes()) > 0: 
                # 선택된 레이어에만 적용되도록...
                clip_pro_count = 0;self.clip_progressBar.setMaximum(len(self.tb_clip_Tiff.selectedIndexes()))
                if os.path.exists(self.txt_output_clip.text() + "/" + str(area) + "/") == False:
                    folder = os.mkdir(self.txt_output_clip.text() + "/" + str(area) + "/")
                
                for idx in self.tb_clip_Tiff.selectedIndexes():
                    # HDF5 수행 후 바로라면.
                    if (self.hdf_convert_tiff != []):
                        tif = self.hdf_convert_tiff[idx.row()]
                        filename = _util.GetFilename(tif)
                        Input = tif.replace(filename, filename + "_Convert")
                    
                        Output = self.txt_output_clip.text() + "/" + str(area) + "/" + filename + "_Clip.tif"
                        try:
#                             arg = "gdal_translate.exe -a_srs epsg:4326 -projwin  " + Clip_area + " -of GTiff " + tif + " " + Output
                            arg = 'gdal_translate.exe -a_srs epsg:4326 -projwin {0} -of GTiff "{0}" "{1}"'.format(Clip_area,tif,Output)   
#                             QgsMessageLog.logMessage(str(arg),"GPM CLIP")
#                             os.system(arg)
#                             arg =[
#                                 osgeo4w,
#                                 "gdal_translate.exe","-a_srs","EPSG:4326",
#                                 "-projwin",Clip_area,"-of","GTiff",tif,Output
#                                 ]
                            sub.call(arg, shell=True)  # 2019-02-25, 전면수정
                            
                            clip_pro_count = clip_pro_count + 1
                            sleep(1)
                            self.clip_progressBar.setValue(clip_pro_count)
                            
                        except Exception as e:
                            QgsMessageLog.logMessage(str(e), "GPM CLIP")
            else:
                _util.MessageboxShowInfo("GPM", "Not Selected Files.")
                return
    
    # ===== 여기는 shape area 선택 함수로 생성...
    def Shape_Clip_apply(self):
#         _util.MessageboxShowInfo("GPM CLIP",str(self.txt_Shape_path.text()))
        if len(self.tb_clip_Tiff.selectedIndexes()) > 0: 
            clip_pro_count = 0;self.clip_progressBar.setMaximum(len(self.tb_clip_Tiff.selectedIndexes()))
            
#             folder = (self.txt_output_clip.text()+"/"+str(os.path.basename(self.txt_Shape_path.text()))+"/").replace("\\","/")
            folder = (self.txt_output_clip.text() + "/shp/").replace("\\", "/")
            if os.path.exists(folder) == False:
                    os.mkdir(folder)
            
            # 여기서 shp의 geometry type은 반드시 폴리곤이여야 합니다 (와카리마스... by.기린)
            vector_polygon = QgsVectorLayer(self.txt_Shape_path.text(), "shp", "ogr")
            vector_polygon.wkbType() == QGis.WKBPolygon
            if (vector_polygon.wkbType() != QGis.WKBPolygon):
                _util.MessageboxShowError("GPM", "Check out the geometry type(polygon) in the shapefile.")
                return
             # polygon이 아니면 메시지로 사용자에게 알립니다.٩(ˊᗜˋ*)و
#             else:
#                 _util.MessageboxShowError("GPM", "Check out the geometry type in the shapefile.")
#                 return
            
            for idx in self.tb_clip_Tiff.selectedIndexes():
                    # HDF5 수행 후 바로라면.
                    if (self.hdf_convert_tiff != []):
                        tif = self.hdf_convert_tiff[idx.row()]
                        filename = _util.GetFilename(tif)
                        
                        Input = tif.replace(filename, filename + "_Convert")
                        Input_layer = gdal.Open(tif)
#                         QgsMessageLog.logMessage(str(Input_layer),"GPM SHP CLIP")
                        clipWidth = (Input_layer.GetGeoTransform()[1])
                        clipHeight = -(Input_layer.GetGeoTransform()[5])
                        Output = folder + filename + "_Clip.tif"
                        try:
            #                             arg = "gdal_translate.exe -a_srs epsg:4326 -projwin  " +Clip_area + " -of GTiff "  +tif+ " " + Output
                            tif = tif.replace("\\", "/")
        #                             arg = "gdalwarp.exe -ot Float32 -q  -of GTiff -tr {0} {1} -tap -cutline ".format(clipWidth,clipHeight)+str(self.txt_Shape_path.text())+" -crop_to_cutline -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 -wo OPTIMIZE_SIZE=TRUE  {0} {1}".format(tif, Output)
#                             arg = "gdalwarp.exe -s_srs EPSG:4326 -q -cutline {0} -crop_to_cutline -tr {1} {2} -of GTiff {3} {4}".format(
#                                 str(self.txt_Shape_path.text()),clipWidth,clipHeight,tif,Output)
                            
                            # 여기 분기가 필요하겠음...prj가 있는 shp는 문제가 없는데
                            # prj가 있는 shp는 문제가 있네
                            
#                             -t_srs EPSG:4326 -tr {1} {2}
#                             arg = 'gdalwarp.exe -s_srs EPSG:4326 -t_srs EPSG:4326 -q -cutline {0} -crop_to_cutline -tr {1} {2} -dstalpha -of GTiff "{3}" "{4}"'.format(
#                                 "\"" + str(self.txt_Shape_path.text()) + "\"", str(clipWidth), str(clipHeight), tif, Output)
                            arg = 'gdalwarp.exe -s_srs EPSG:4326 -t_srs EPSG:4326 -q -cutline "{0}" -crop_to_cutline -tr {1} {2} -dstalpha -of GTiff "{3}" "{4}"'.format(
                                str(self.txt_Shape_path.text()),str(clipWidth),str(clipHeight),tif,Output)

#                             clip_call = [osgeo4w,
#                                          "gdalwarp.exe","-q","-cutline",str(self.txt_Shape_path.text()),
#                                          "-crop_to_cutline",
#                                          "-tr",str(clipWidth),str(clipHeight),"-of","GTiff",tif,Output]
#                             arg = [osgeo4w,"gdalwarp.exe",
#                                          "-s_srs","EPSG:4326",
#                                          "-q","-cutline",str(self.txt_Shape_path.text()),
#                                          "-crop_to_cutline","-tr",str(clipWidth),str(clipHeight),"-dstalpha","-of","GTiff",tif,Output]
#                             QgsMessageLog.logMessage(str(arg),"GPM CLIP")
                            sub.call(arg, shell=True)  # 2019-02-25 전면 교체
#                             QgsMessageLog.logMessage(str(callvalue),"GPM CLIP")
#                             os.system(arg)
                            clip_pro_count = clip_pro_count + 1
                            sleep(1)
                            self.clip_progressBar.setValue(clip_pro_count)
                            
                        except Exception as e:
                            QgsMessageLog.logMessage(str(e), "GPM CLIP")
        
        else:
            # 파일 선택하라니까...
            _util.MessageboxShowInfo("GPM", "Not Selected Files.")
            return
    
    # ==== 사용자 직접area 입력
    # 숫자인지 여부도 판단.. 숫자만 받아요. 감사
    def isNumber(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def user_clip_zone(self):
    # 만약 1.x,y 2.x,y 텍스트 박스가 빈칸이면 return
        self.clip_x1 = str(self.clip_1_x.text()); self.clip_y1 = str(self.clip_1_y.text())
        self.clip_x2 = str(self.clip_2_x.text()); self.clip_y2 = str(self.clip_2_y.text())
         # 빈칸이면 안돼
        if self.clip_x1.strip() == "":
            _util.MessageboxShowInfo("GPM", "The clip zone is not set.")
            self.clip_1_x.setFocus()
            return
        if self.clip_y1.strip() == "":
            _util.MessageboxShowInfo("GPM", "The clip zone is not set.")
            self.clip_1_y.setFocus()
            return
        if self.clip_x2.strip() == "":
            _util.MessageboxShowInfo("GPM", "The clip zone is not set.")
            self.clip_2_x.setFocus()
            return
        if self.clip_y2.strip() == "":
            _util.MessageboxShowInfo("GPM", "The clip zone is not set.")
            self.clip_2_y.setFocus()
            return
        
        # 숫자인지 여부도 판단.. 숫자만 받아요. 감사
        if self.isNumber(self.clip_x1) == False:
            _util.MessageboxShowInfo("GPM", "Input number")
            self.clip_1_x.setFocus()
            return
        if self.isNumber(self.clip_x2) == False:
            _util.MessageboxShowInfo("GPM", "Input number")
            self.clip_2_x.setFocus()
            return
        if self.isNumber(self.clip_y1) == False:
            _util.MessageboxShowInfo("GPM", "Input number")
            self.clip_1_y.setFocus()
            return
        if self.isNumber(self.clip_y2) == False:
            _util.MessageboxShowInfo("GPM", "Input number")
            self.clip_2_y.setFocus()
            return    
            
    def user_Clip_apply(self):
        self.user_clip_zone()
        
        Clip_area = "{0} {1} {2} {3}".format(str(self.clip_x1), str(self.clip_y2), str(self.clip_x2), str(self.clip_y1))
        
        if len(self.tb_clip_Tiff.selectedIndexes()) > 0: 
            clip_pro_count = 0;self.clip_progressBar.setMaximum(len(self.tb_clip_Tiff.selectedIndexes()))
             
#             folder = (self.txt_output_clip.text()+"/"+str(os.path.basename(self.txt_Shape_path.text()))+"/").replace("\\","/")
            folder = (self.txt_output_clip.text() + "/User_CLIP/").replace("\\", "/")  # 폴더명 임의 지정
            if os.path.exists(folder) == False:
                    os.mkdir(folder)
#             
            for idx in self.tb_clip_Tiff.selectedIndexes():
                    # HDF5 수행 후 바로라면.
                    if (self.hdf_convert_tiff != []):
                        tif = self.hdf_convert_tiff[idx.row()]
                        filename = _util.GetFilename(tif)
#                         
                        Input = tif.replace(filename, filename + "_Convert")
                        Output = folder + filename + "_Clip.tif"
                        try:
#                             arg = "gdal_translate.exe -a_srs epsg:4326 -projwin  " +Clip_area + " -of GTiff "  +tif+ " " + Output
                            tif = tif.replace("\\", "/")
#                             arg = "gdal_translate.exe -a_srs EPSG:4326 -projwin  " + Clip_area + " -of GTiff " + tif + " " + Output
                            arg = 'gdal_translate.exe -a_srs EPSG:4326 -projwin  {0} -of GTiff "{1}" "{2}"'.format(str(Clip_area),tif,Output)
#                             arg = [
#                                 osgeo4w, "gdal_translate.exe",
#                                "-a_srs","EPSG:4326","-projwin",
#                                Clip_area,"-of","GTiff",tif,Output             
#                                 ]
                            sub.call(arg, shell=True)  # 2019-02-25, 전면교체
#                             QgsMessageLog.logMessage(str(arg),"GPM CLIP")
#                             os.system(arg)
                            clip_pro_count = clip_pro_count + 1
                            sleep(1)
                            self.clip_progressBar.setValue(clip_pro_count)
                             
                        except Exception as e:
                            QgsMessageLog.logMessage(str(e), "GPM CLIP")
        
        else:
            #선택 !@ ㅅ선택하세요!!! 꼮!!!!
            _util.MessageboxShowInfo("GPM", "Not Selected Files.")
            return    
    
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
            if str_Input_folder.strip() == "":
                _util.MessageboxShowInfo("GPM", "Select Directory")
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

            if str_output_folder.strip() == "":
                _util.MessageboxShowInfo("GPM", "Select Directory")
                self.txt_output_utm.setFocus()
                return
            
            UTM_Tiff_file_List = _util.GetFilelist(str_Input_folder, "tif")
            self.utm_progressBar.setValue(0)
            self.utm_progressBar.setMaximum(len(UTM_Tiff_file_List))
            
            # 좌표계 변환 실시
            self.Convert_utm(UTM_Tiff_file_List)
            
        except Exception as es:
            _util.MessageboxShowError("Error message", str(es))

    # 좌표계 변환
    def Convert_utm(self, list):
        os.environ['GDAL_DATA'] = 'C:\Program Files\QGIS 2.18\share'
        
        try:
#             source=self.cmb_utm_source.currentText()
            target = self.cmb_utm_target.currentText()
#             s_srs = _Dict.UTM_dic[str(source)]
            t_srs = _Dict.UTM_dic[str(target)]

            utm_count = 0
            for file in list:
                filename = _util.GetFilename(file)
                Output = self.txt_output_utm.text() + "/" + filename + "_UTM.tif" 
#                 
#                 file.replace(filename, filename + "_UTM")
#                 path ="‪C:/Program Files/GDAL/gdalwarp.exe"
#                 arg =path+ " -overwrite -s_srs "+ "\"" + s_srs +"\""+ " -t_srs "+"\"" + t_srs +"\"" + "-of GTiff "
# #                 gdalwarp.exe -s_srs " + " " + s_srs +" -t_srs " + " "+t_srs + " "
#                 arg = arg +" "+ file +" " + Output
                
                # gdalwarp.exe가 QGIS에도 있으므로... 굳이 경로 다 안써도 됨..;; _ JO                
                arg = 'gdalwarp -overwrite -t_srs ' + "\"" + t_srs + "\"" + (' -of GTiff "{0}" "{1}"').format(file, Output)
                
                exe = _util.Execute(arg)
                if (exe != 0):
                    _util.MessageboxShowInfo("GPM", "Failed to perform normally.")
                    self.utm_progressBar.setValue(0)
                    break
                elif (exe == 0): 
                    sleep(1)
                    utm_count = utm_count + 1
                    self.utm_progressBar.setValue(utm_count)
                    sleep(1)
                
#             _util.MessageboxShowInfo("GPM","Complete convert UTM.")
#                 _util.ConvertUTM(file,Output,s_srs,t_srs)
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))

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
                Resample_folder_list = _util.GetFilelist(Input_folder, "tif")

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
                resample_count = 0
                
                check_Folder = _util.CheckFolder(output_folder)
                QgsMessageLog.logMessage(str(check_Folder), "GPM Resample")
                
                for file in Resample_folder_list:
                    filename = _util.GetFilename(file)
                    Output = output_folder + "/" + filename + "_resample.tif"
    #                 file.replace(filename,filename+"_resample")
#                     arg = "gdalwarp.exe -r "+str(Method)+" -tr "+str(cellvalue) +" "+str(cellvalue) + " -of GTiff " + "\""+str(file)+"\""+" \""+str(Output)+"\""
                    arg = 'gdalwarp.exe -r {0} -tr {1} {1} -of GTiff "{2}" "{3}"'.format(str(Method), str(cellvalue), str(file), str(Output))
#                     exe = _util.Execute(arg)
                    exe = sub.call(arg, shell=True)
#                     exe =_util.ExecuteGridResampling(Method,cellvalue,"\""+file+"\"","\""+Output+"\"")
                    QgsMessageLog.logMessage(str(exe), "GPM Resample")
                    
                    if (exe == 0):
                        sleep(0.5)
                        resample_count = resample_count + 1
                        self.resampling_progressBar.setValue(resample_count)
                        sleep(0.5)
                    
                    else:
                        _util.MessageboxShowInfo("GPM", "Failed to perform normally.")
                        self.resampling_progressBar.setValue(0)
                        break
            except Exception as e:
                _util.MessageboxShowError("GPM", str(e))    
        except Exception as ex:
            _util.MessageboxShowError("GPM", str(ex))

    # =============== ACCUM ===========================================
    def select_files(self):
        try: 
            self.tlb_filelist_Accum.clear()  # 초기화
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
            
            count = 0; self.accum_list = []
            for file in FileList:
                self.tlb_filelist_Accum.insertRow(count)
                self.tlb_filelist_Accum.setItem(count, 0, QTableWidgetItem(str(file)))
                self.accum_list.append(str(file))
                count = count + 1
                
            # 프로그레스바 신설.. 내가 불편해서 만들었음
            self.acc_progressBar.setValue(0)
            self.acc_progressBar.setMaximum(len(self.accum_list))
                
        except Exception as e:
            _util.MessageboxShowInfo("GPM", str(e))
            
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
            if accum_output.strip() == "":
                _util.MessageboxShowInfo("GPM", "The folder path is not set.")
                self.txt_output_accum.setFocus()
                return           
            
            # 2018-10-26 필요없는 부분 제거
#             self.accum_rows=[];
#             if len(self.tlb_filelist_Accum.selectedIndexes())>0:
#                 for s_idx in self.tlb_filelist_Accum.selectedIndexes():
#                     self.accum_rows.append(s_idx.row())
#             else:
#                 _util.MessageboxShowError("GPM", "No columns selected or no layers.")
#                 return
#             QgsMessageLog.logMessage(str(band),"GPM ACCUM")
            
            # Accum 기능
            accum_run = self.Accum_Tiff()
            
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))
    
    def Accum_Tiff(self):
        # 환경 설정 
        saga_ltr = os.environ["SAGA"] = 'c://PROGRA~1/QGIS2~1.18/apps/saga-ltr'
        saga_modules = os.environ["SAGA_MLB"] = 'c://PROGRA~1/QGIS2~1.18/apps/saga-ltr/modules'
        PATH = os.environ["PATH"] = 'c://PROGRA~1/QGIS2~1.18/apps/Python27/lib/site-packages/Shapely-1.2.18-py2.7-win-amd64.egg/shapely/DLLs;c://PROGRA~1/QGIS2~1.18/apps/Python27/DLLs;c://PROGRA~1/QGIS2~1.18/apps/Python27/lib/site-packages/numpy/core;c://PROGRA~1/QGIS2~1.18/apps/qgis-ltr/bin;c://PROGRA~1/QGIS2~1.18/apps/Python27/Scripts;c://PROGRA~1/QGIS2~1.18/bin;c://WINDOWS/system32;c://WINDOWS;c://WINDOWS/system32/WBem;c://PROGRA~1/QGIS2~1.18/apps/saga-ltr;c://PROGRA~1/QGIS2~1.18/apps/saga-ltr/modules'
        
        try:
#             self.accum_band_list = []
            self.Accum_Amount()
        except Exception as e:
            _util.MessageboxShowError("GPM Accum", str(e))
    
    def Accum_Amount(self):
        try:
            self.amount_list = []
            # 자꾸 꼬이는 것 같아서
            pro_count = 0
            for filelist in self.accum_list:
                if os.path.exists(self.txt_output_accum.text() + "/Amount/") == False:
                    os.mkdir(self.txt_output_accum.text() + "/Amount/")
                    
                filename = _util.GetFilename(filelist)
                Output_Amount = self.txt_output_accum.text() + "/Amount/" + filename + "_Amount.tif"
                amount = _utilAC.accum_amount(filelist, Output_Amount)
                self.amount_list.append(str(Output_Amount))
                pro_count = pro_count + 1
                self.acc_progressBar.setValue(pro_count / 2)
                
            self.accum_check(self.amount_list)
            sleep(0.5)
            self.acc_progressBar.setValue(len(self.accum_list))
#             _util.MessageboxShowInfo("GPM", "Finish.")
#             for file2 in self.amount_list:   
#                 filename2 = _util.GetFilename(file2)
                # Accum
#                 Output_Accum = self.txt_output_accum.text() + "/"+filename2+"_Accum.tif"
#                 Output_Accum = filename2+"_Accum"
            # 아주 비효율 적이지만 목표는 되기만 하면 되거든
            
        except Exception as e:
            _util.MessageboxShowInfo("GPM Amount", str(e))
                
    def accum_check(self, list):
#         gdal_calc = os.path.dirname(os.path.abspath(__file__))+"/Lib/gdal_calc.py"
#         gdal_calc = "‪C:\Program Files\QGIS 2.18\bin\gdal_calc.py"
        
        try:
            # 2018-10-17 JO : 라디오 버튼이 아닌 체크박스로 중복 수행 가능토록 변경
            if self.chk_Accum_1H.isChecked():
    #         if self.rdo_Accum_1H.isChecked():
                H1hour_list = []
                if os.path.exists(self.txt_output_accum.text() + "/1H/") == False:
                    os.mkdir(self.txt_output_accum.text() + "/1H/")
                
                for f_accum in list:
                    filename = _util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text() + "/1H/" + filename + "_1H.tif"
                    H1hour_list.append(f_accum)
                    if len(H1hour_list) > 2:
                        del H1hour_list[1], H1hour_list[0]
                    if len(H1hour_list) == 2:
#                         QgsMessageLog.logMessage(str(H1hour_list),"GPM Accum Run 1H")
                        _utilAC.Accum_hour(H1hour_list, outputname)
                        
            #============ 3h ===========
            if self.chk_Accum_3H.isChecked():
                H3hour_list = []
                if os.path.exists(self.txt_output_accum.text() + "/3H/") == False:
                    os.mkdir(self.txt_output_accum.text() + "/3H/")
                    
                for f_accum in list:
                    filename = _util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text() + "/3H/" + filename + "_3H.tif"    
                    H3hour_list.append(f_accum)
                    if len(H3hour_list) > 6:
                        del H3hour_list[5], H3hour_list[4], H3hour_list[3], H3hour_list[2], H3hour_list[1], H3hour_list[0]
                        
                    if len(H3hour_list) == 6:
#                         QgsMessageLog.logMessage(str(H3hour_list),"GPM Accum Run 3H")
                        _utilAC.Accum_hour(H3hour_list, outputname)
                    
#     #         if self.rdo_Accum_3H.isChecked():
#                 outputname = self.txt_output_accum.text()+"/3H/"+output+"_3H.tif"
#                 _utilAC.Accum_hour("3H",list,outputname)
#             
            #=============== 6H===================
            if self.chk_Accum_6H.isChecked():
                H6hour_list = []
                if os.path.exists(self.txt_output_accum.text() + "/6H/") == False:
                    os.mkdir(self.txt_output_accum.text() + "/6H/")
                    
                for f_accum in list:
                    filename = _util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text() + "/6H/" + filename + "_6H.tif"    
                    H6hour_list.append(f_accum)
                    if len(H6hour_list) > 12:
                        del H6hour_list[11], H6hour_list[10], H6hour_list[9], H6hour_list[8], H6hour_list[7],
                        H6hour_list[6], H6hour_list[5], H6hour_list[4], H6hour_list[3], H6hour_list[2], H6hour_list[1], H6hour_list[0]
                        
                    if len(H6hour_list) == 12:
#                         QgsMessageLog.logMessage(str(H6hour_list),"GPM Accum Run 6H")
                        _utilAC.Accum_hour(H6hour_list, outputname)
                
            #=============== 9H===================
            if self.chk_Accum_9H.isChecked():
                H9hour_list = []
                if os.path.exists(self.txt_output_accum.text() + "/9H/") == False:
                    os.mkdir(self.txt_output_accum.text() + "/9H/")
                    
                for f_accum in list:
                    filename = _util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text() + "/9H/" + filename + "_9H.tif"    
                    H9hour_list.append(f_accum)
                    if len(H9hour_list) > 18:
                        del H9hour_list[17], H9hour_list[16], H9hour_list[15], H9hour_list[14], H9hour_list[13], H9hour_list[12],
                        H9hour_list[11], H9hour_list[10], H9hour_list[9], H9hour_list[8], H9hour_list[7], H9hour_list[6], H9hour_list[5],
                        H9hour_list[4], H9hour_list[3], H9hour_list[2], H9hour_list[1], H9hour_list[0]
                    if len(H9hour_list) == 18:
#                         QgsMessageLog.logMessage(str(H9hour_list),"GPM Accum Run 9H")
                        _utilAC.Accum_hour(H9hour_list, outputname)
            #=============== 12H===================
            if self.chk_Accum_12H.isChecked():
                H12hour_list = []
                if os.path.exists(self.txt_output_accum.text() + "/12H/") == False:
                    os.mkdir(self.txt_output_accum.text() + "/12H/")
                
                for f_accum in list:
                    filename = _util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text() + "/12H/" + filename + "_12H.tif"       
                
                    if len(H12hour_list) > 24:
                        H12hour_list.append(f_accum)
                        del H12hour_list[23], H12hour_list[22], H12hour_list[21], H12hour_list[20], H12hour_list[19], H12hour_list[18], H12hour_list[17],
                        H12hour_list[16], H12hour_list[15], H12hour_list[14], H12hour_list[13], H12hour_list[12], H12hour_list[11], H12hour_list[10], H12hour_list[9], H12hour_list[8],
                        H12hour_list[7], H12hour_list[6], H12hour_list[5], H12hour_list[4], H12hour_list[3], H12hour_list[2], H12hour_list[1], H12hour_list[0]
                    if len(H12hour_list) == 24:
                        _utilAC.Accum_hour(H12hour_list, outputname)
                    
            #=============== 24H===================
            if self.chk_Accum_24H.isChecked():
                H24hour_list = []
                if os.path.exists(self.txt_output_accum.text() + "/24H/") == False:
                    os.mkdir(self.txt_output_accum.text() + "/24H/")
                for f_accum in list:
                    filename = _util.GetFilename(f_accum)
                    outputname = self.txt_output_accum.text() + "/24H/" + filename + "_24H.tif"   
                    
                    if len(H24hour_list) > 48:
                        H24hour_list.append(f_accum)
                        del H24hour_list[47], H24hour_list[46], H24hour_list[45], H24hour_list[44], H24hour_list[43], H24hour_list[42], H24hour_list[41], H24hour_list[40], H24hour_list[39],
                        H24hour_list[38], H24hour_list[37], H24hour_list[36], H24hour_list[35], H24hour_list[34], H24hour_list[33], H24hour_list[32], H24hour_list[31], H24hour_list[30], H24hour_list[29],
                        H24hour_list[28], H24hour_list[27], H24hour_list[26], H24hour_list[25], H24hour_list[24], H24hour_list[23], H24hour_list[22], H24hour_list[21], H24hour_list[20], H24hour_list[19],
                        H24hour_list[18], H24hour_list[17], H24hour_list[16], H24hour_list[15], H24hour_list[14], H24hour_list[13], H24hour_list[12], H24hour_list[11], H24hour_list[10], H24hour_list[9],
                        H24hour_list[8], H24hour_list[7], H24hour_list[6], H24hour_list[5], H24hour_list[4], H24hour_list[3], H24hour_list[2], H24hour_list[1], H24hour_list[0]
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
            
            if Input_file.strip() == "":
                _util.MessageboxShowInfo("GPM", "Select shp file ")
                self.txt_csv_shp.setFocus()
                return
            
            # 나온 값을 csv 파일로 내보내면 됨.
            if output_file.strip() == "":
                _util.MessageboxShowInfo("GPM", "Select Save file name ")
                self.txt_shp_field.setFocus()
                return
            
            # 여기서 중요 포인트는 shape 파일은 반드시 좌표계를 지니고 있어야함(prj 파일) 
#             v_layer =QgsVectorLayer(Input_file,"SHP","ogr")
            
#             if get_field.strip() =="":
#                 _util.MessageboxShowInfo("GPM", "The FieldName is not set.")
#                 self.txt_fieldname_shp.setFocus()
#                 return  
#             QgsMessageLog.logMessage(str(self.cmb_FieldAtt.currentText()),"GPM CSV")
            try:
#                 self.read_SHP(v_layer)
                # 2018-11-09 : 헤더가 존재하면 파일을 생성하고 없으면 생성하지 않음
                self.csv_file = open(output_file, 'w+')
                self.csv_file.write("filename")
#                 get_shape_fieldname = self.get_shape_coord(v_layer,(self.txt_fieldname_shp.text()))
                get_shape_fieldname = self.get_shape_coord((self.cmb_FieldAtt.currentText()))
                # lOG
                # QgsMessageLog.logMessage(str(get_shape_fieldname),"GPM MAKE CSV")
                
#                 #2018-11-09 : get_shape_fieldname 이 정상 수행 되었을 때 다음 수행    
                if get_shape_fieldname == True:
                    cell_values = self.shape_coord_raster_cellvalue(self.filenames)
                    self.csv_file.close() 
                    _util.MessageboxShowInfo("Make CSV", "Make CSV Function Completed.")
                    
            except Exception as e:
                _util.MessageboxShowInfo("GPM", str(e))
#             field_name=self.get_shape_field(v_layer,self.txt_fieldname_shp.text())
            
            # 2018-11-09 : get_shape_fieldname 이 None인 경우 생성되었던 csv_file 제거한다.
            if get_shape_fieldname == False:
                self.csv_file.close()    
                os.remove(output_file)
                return
            
#             _util.ConvertShapeToCSV(Input_file,output_file)
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))
     
    # 20189-03-07 : SHP를 읽기만하는 곳.
    def read_SHP(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'c://', "Shape files (*.shp)")
        if _util.CheckFile(fname):
            self.txt_csv_shp.setText(fname)
            
        v_layer = QgsVectorLayer(fname, "SHP", "ogr")
        prov = (v_layer).dataProvider()
        self.features = (v_layer).getFeatures()
        # 필드 이름
        self.fieldNames = []
        fields = prov.fields()
#         fields = prov.fields()
        for field in fields:
            # txt가 아닌 콤보 박스에 세팅되도로고 함..
#             self.fieldNames.append( ((str(field.name())).upper()))
            self.fieldNames.append(str(field.name()))
        self.cmb_FieldAtt.addItems(self.fieldNames)
    
    # 2018-10-19 : shape의 좌표, 필드 이름의 값 가져오기.
#     def get_shape_coord(self,shapefile,txt):    
    def get_shape_coord(self, txt):    
#         v_layer =QgsVectorLayer(shapefile,"SHP","ogr")
        
#         prov = shapefile.dataProvider()
#         features = shapefile.getFeatures()
#         
#         #필드 이름
#         fieldNames = []
# #         fields = prov.fields()
#         for field in self.fields:
#             fieldNames.append( ((str(field.name())).upper()))
            
#         for name in fieldNames:
#             if (name == txt):
#                 QgsMessageLog.logMessage(str(name),"GPM CSV 1")
#                 self.csv_file.write(str(name))
        try:
            self.point_list = []         
            # 필드 값이 있는 것이면 수행. 없으면 msg
            if ((txt.upper())) not in (self.fieldNames):
                _util.MessageboxShowInfo("GPM", "No have FieldName")
                # 2018-11-09 msg 출력 후 에 진행 X, return으로 stop 시킴      
                return False
    
    #         if ((txt.upper())) in fieldNames:
            if (txt.upper()) in (self.fieldNames):
                for feat in (self.features):
                    # 좌표값
                    geom = feat.geometry()
                    self.point_list.append(geom.asPoint())
    #                 QgsMessageLog.logMessage(str((feat[(((txt.upper()).decode('cp949').encode('utf-8')))])),"GPM CSV")
                    # 필드 값
        #             QgsMessageLog.logMessage(str(feat[txt]),"GPM CSV 1")
    #                 self.csv_file.write(","+str(feat[(((txt.upper()).decode('cp949').encode('utf-8')))]))
                    self.csv_file.write("," + str(feat[(txt.upper())]))
            return True
        except Exception as exc:
            _util.MessageboxShowError("GPM CSV", str(exc))
                
    # shape 좌표 위치의 래스터 셀 값 가져오기
    # 래스터 선택해야 함.
    def shape_coord_raster_cellvalue(self, raster):
        try:
            for r_layer in raster:
                self.csv_file.write("\n" + r_layer)
                layer = QgsRasterLayer(r_layer)
                pixelWidth = layer.rasterUnitsPerPixelX()
                pixelHeight = layer.rasterUnitsPerPixelY()
                 
                for x, y in self.point_list:
                    ident = layer.dataProvider().identify(QgsPoint(x, y), QgsRaster.IdentifyFormatValue)
                    if ident.isValid():
    #                     QgsMessageLog.logMessage(str(ident.results()[1]),"GPM CSV 2")
                        self.csv_file.write("," + str(ident.results()[1]))
            
    #                     return str(ident.results()[1])
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))

   # =======================Funtion=======================================
    def select_files_func(self):
        try: 
            self.tlb_Function.clear()  # 초기화
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
#                 self.tlb_Function.setItem(count, 0, QTableWidgetItem(str(file)+"@1"))
                self.tlb_Function.setItem(count, 0, QTableWidgetItem(file))
                self.func_list.append(file)
                count = count + 1
                
            # 테이블 데이터 수정 못하게 옵션
            self.tlb_Function.setEditTriggers(QTableWidget.NoEditTriggers)

        except Exception as e:
            _util.MessageboxShowInfo("GPM", str(e))
    
    def Fun_apply_Click(self):
        # 아무래도 파일 불러오는 기능이 따로 있어야 하나 봅니다... 지금 제 눈에 이게 제일 쉬워보이니 이걸 먼저 해볼까요
        
        try:
            if "X".lower() in (self.txt_function_txt.text()):
                   calculus = "(" + (self.txt_function_txt.text()).replace("X".lower(), "X@1").replace("&", "and") + "*1)+0"
                   calculus2 = (self.txt_function_txt.text()).replace("X".lower(), "A")
                   QgsMessageLog.logMessage(str(calculus2), "GPM FUNC")
                   
            path = self.txt_output_fun.text()
              
#             폴더 채택이 아닌 파일 단위로 결과 출력...
#             ☆★☆★ 2018-08-20 : 경로가 존재하지 않으면 오류 반환 ☆★☆★
            isPath = os.path.dirname(path)
            if os.path.isdir(isPath) == False:
                _util.MessageboxShowError("GPM", "This directory does not exist.")
                self.txt_output_fun.setFocus()
                return
               
            # 수식 칸이 빈칸이면 오류 반환
            if self.txt_function_txt.text().strip() == "":
                _util.MessageboxShowError("GPM", "The Operation you entered is incorrect or missing.")
                self.txt_function_txt.setFocus()
                return
            
            # 여기서 선택한 레이어들만 식 적용되도록!
            select_list = []
            for idx in self.tlb_Function.selectedIndexes():
                select_list.append(self.func_list[idx.row()])
#                 QgsMessageLog.logMessage(str(self.func_list[idx.row()]),"GPM FUNC")
                                    # gdal calc로 바꾸고 싶어요..
                tiff_ds = gdal.Open(str(self.func_list[idx.row()]))
                Nodata = tiff_ds.GetRasterBand(1) .GetNoDataValue()
                QgsMessageLog.logMessage(str(Nodata), "GPM FUNC")
                  
                call_arg = [osgeo4w,
                            "gdal_calc",
                            "-A", str(self.func_list[idx.row()]), "--format", "GTiff", "--calc", str(calculus2),
                            "--outfile", str(path + "/" + str(os.path.basename(self.func_list[idx.row()])) + "_function.tif"), "--NoDataValue", str(Nodata)]
                QgsMessageLog.logMessage(str(call_arg), "GPM FUNC")
                sub.call(call_arg, shell=True)
               
#             for lyr in (self.func_list):
#                 ras = QgsRasterCalculatorEntry()
#                 ras.ref = "X@1"
#                 ras.raster = lyr
#                 ras.bandNumber = 1
#                 entries.append( ras )
#                 QgsMessageLog.logMessage(str(entries),"gpm func")
#                 if (lyr.name()) in select_list:
#                     ras.ref = lyr.name()+"@1"
                    
#             entries = [] #참조된 레이어 리스트
#             for lyr in _layers:
# #                 calculus="("+self.txt_function_txt.text().replace("&", "and")+"*1)+0"
#                 
#                 
#                 ras = QgsRasterCalculatorEntry()
#                 if (lyr.name()) in select_list:
#                     QgsMessageLog.logMessage(str(lyr.name()),"GPM FUNC")
#                 ras.ref = lyr.name()+"@1"
#                     ras.ref = "X@1"
#                     ras.raster = lyr
#                     ras.bandNumber = 1
#                     entries.append( ras )
# #        
# #                     #calc = QgsRasterCalculator( '(ras@1 / ras@1) * ras@1', path + lyr.name() + "_suffix.tif", 'GTiff', lyr.extent(), lyr.width(), lyr.height(), entries )
#                     calc = QgsRasterCalculator( calculus, path+"/"+lyr.name()+"_function.tif", 'GTiff', _layers[0].extent(), _layers[0].width(), _layers[0].height(), entries )
#                     calc.processCalculation()
                    
            _util.MessageboxShowInfo("GPM", "Complete Raster Calculator.")
        except Exception as e:
            _util.MessageboxShowInfo("GPM", str(e))
       
    # table 셋팅
    def Set_table_list_fun(self):
        self.tlb_Function.setColumnCount(1)
        self.tlb_Function.setHorizontalHeaderLabels(["Layer List"])
        stylesheet = "QHeaderView::section{Background-color:rgb(174, 182, 255, 100)}"
        self.tlb_Function.setStyleSheet(stylesheet)

        count = 0 ; self.func_list = []
        for layer in _layers:
            self.tlb_Function.insertRow(count)
            self.tlb_Function.setItem(count, 0, QTableWidgetItem(layer.name() + "@1"))
            self.func_list.append(layer.name())
            count = count + 1

        # 테이블 데이터 수정 못하게 옵션
        self.tlb_Function.setEditTriggers(QTableWidget.NoEditTriggers)
        
    # 임시 기능 완료
    # =============== ASC ===============================================
    
    #======= ASC FILE SELECT ===========
    def select_ASC_files(self):
        # dir = os.path.dirname(sys.argv[0])
#         self.ASC_files = QFileDialog.getOpenFileNames(self,"Select Input FILES",dir,"GRM Project xml files (*.tif)",options=QtGui.QFileDialog.DontUseNativeDialog)
        self.ASC_files = QFileDialog.getOpenFileNames(self, "Select Input FILES", 'c://', "GRM Project xml files (*.tif)")
        self.txt_input_asc.setText(os.path.dirname(self.ASC_files[0]) + " || select count : " + str(len(self.ASC_files)))
    
    #======= ASC APPLY=============
    def ASC_apply_Click(self):
        try:
            str_Input_file = self.ASC_files
            
            # 파일 선택이 안되어 있으면 다믐 메시지 반환
#             if str_Input_file.strip() == "":
            if len(str_Input_file) == 0:
                _util.MessageboxShowInfo("GPM", "Select Tif file ")
                self.txt_input_asc.setFocus()
                return
            
            # output 폴더 지정 안되어 있거나 폴더 경로가 올바르지 않을 경우 다음 메시지 반환
            if os.path.isdir(self.txt_output_asc.text()) == False:
                _util.MessageboxShowError("GPM Make ASC", "This directory does not exist.")
                self.txt_output_asc.setFocus()
                return
            
            i = 0 ; count_pro_asc = 1; self.asc_progressBar.setValue(0); self.asc_progressBar.setMaximum(len(str_Input_file))
            # arg = "gdal_translate.exe"
            for asc in str_Input_file:
                filename = _util.GetFilename(asc)
                output_filename = self.txt_output_asc.text() + ("/{0}.asc").format(filename)
                
#                 QgsMessageLog.logMessage(str(i) + " : "+ str(asc), "GPM CONVERT ASC")
#                 QgsMessageLog.logMessage(str(i) + " : "+ str(output_filename), "GPM CONVERT ASC")
#                 i=i+1
                
                _util.ConvertRasterToASC(asc, output_filename)
                sleep(1)
                self.asc_progressBar.setValue(count_pro_asc)
                count_pro_asc = count_pro_asc + 1
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
        Data_icon = path + '\image\data.png'  # TEST
        icon = QtGui.QIcon(Data_icon)
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

    def MoveUp(self, table):
        row = table.currentRow()
        column = table.currentColumn()
        if row > 0:
            table.insertRow(row - 1)
            for i in range(table.columnCount()):
                table.setItem(row - 1, i, table.takeItem(row + 1, i))
                table.setCurrentCell(row - 1, column)
            table.removeRow(row + 1)

    def MoveDown(self, table):
        row = table.currentRow()
        column = table.currentColumn()
        if row >= 0:
            if row < table.rowCount() - 1:
                table.insertRow(row + 2)
                for i in range(table.columnCount()):
                    table.setItem(row + 2, i, table.takeItem(row, i))
                    table.setCurrentCell(row + 2, column)
                table.removeRow(row)

    def ReMove(self, table):
        row = table.currentIndex().row()
        mess = "Are you sure you want to delete the selected items?"
        result = QMessageBox.question(None, "Watershed Setup", mess, QMessageBox.Yes, QMessageBox.No)
        if result == QMessageBox.Yes:
            table.removeRow(row)
#             2018-09-10 JO : 목록에 표시만 제거될 뿐 내부적으로 적용 안됨.

    # 버튼 아이콘 
    def set_btn_icon(self):
        # btn_Apply 버튼의 아이콘 넣기
        btn_apply_icon = os.path.dirname(os.path.abspath(__file__)) + "/icon/bottom_arrow.png"
        self.btn_Apply.setIcon(QtGui.QIcon(btn_apply_icon))
        
        # kict_logo 박아넣음.
        kict_logo = os.path.dirname(os.path.abspath(__file__)) + "/icon/GPM_developer_small.png"
#         self.kict_logo.setIcon(QtGui.QIcon(kict_logo))
        self.kict_logo.setPixmap(QtGui.QPixmap(kict_logo))

    # 레이어 목록 혹은 파일 목록사용여부 라디오버튼
    def Select_radio_event(self):
        if self.rdo_Layer.isChecked():
            self.txt_Input_data.setDisabled(True)
            self.btnOpenDialog_Input.setDisabled(True)
            # QGIS 레이어 목록을 리스트 박스에 셋팅 하기
            self.Set_Listbox()
        else:
#             self.txt_Input_data.setDisabled(False)
            self.txt_Input_data.setDisabled(True)
            self.btnOpenDialog_Input.setDisabled(False)

    # Qgis Layer 목록 리스트 뷰에 넣기
    def Set_Listbox(self):
        global _ASC_filename
        # del _ASC_filename[:]
        self.lisw_ASC.setRowCount(0)
        for row in (_ASC_filename):
            counts = self.lisw_ASC.rowCount()
            self.lisw_ASC.insertRow(counts)
            self.lisw_ASC.setItem(counts, 0, QTableWidgetItem(row))

    # 사용자가 ASC 파일경로를 다이얼 로그로 받아 오는 부분
    def Select_ASC_event(self):
        # 2018-05-08:수정
        # 리스트 초기화
        self.lisw_ASC.setRowCount(0)
        global _ASC_filename
        del _ASC_filename[:]

        # dir = os.path.dirname(sys.argv[0])
        try:
            # 사용자가 선택한 파일 목록
            # _ASC_filename = QFileDialog.getOpenFileNames(self,"Select Input ASC FILES",dir,"*.asc *.ASC ",options=QtGui.QFileDialog.DontUseNativeDialog)
            _ASC_filename = QFileDialog.getOpenFileNames(self, "Select Input ASC FILES", 'c://', "*.asc *.ASC ")
            
            # btnOpenDialog_Input에 선택한 파일들의 폴더 경로 넣기
            self.txt_Input_data.setText(os.path.dirname(_ASC_filename[0]))
            
            # 선택된 파일들을 리스트 박스에 넣기
            for row in (_ASC_filename):
                counts = self.lisw_ASC.rowCount()
                self.lisw_ASC.insertRow(counts)
                self.lisw_ASC.setItem(counts, 0, QTableWidgetItem(row))
            # _util.MessageboxShowInfo("Satellite", str(len(_ASC_filename))+" FILES SELECTED")
        except Exception as e:
            _util.MessageboxShowError("Satellite", " A file selection error occurred. ")
            return

    # CSV 선택파일 다이얼로그
    def Select_CSV_event(self):
        # 기본 경로
        dir = os.path.dirname(sys.argv[0])
        global select_file, select_file_path
        
        try:
            # 파일은 하나만 선택하게 함.
            select_file = QFileDialog.getOpenFileName(self, "Select csv file.", dir, '*.csv *.CSV', options=QtGui.QFileDialog.DontUseNativeDialog)
            # 기존 2017버전으로 복귀
#             select_file = QFileDialog.getOpenFileNames(self, "Select csv files.", dir, '*.csv *.CSV',options=QtGui.QFileDialog.DontUseNativeDialog)
            select_file_path = os.path.dirname(select_file)
            self.txt_Convert_path.setText(str(select_file))
            # 선택한 csv 파일의 폴더경로를 받음
#             self.txt_Convert_path.setText(str(os.path.dirname(select_file[0])))
#             self.list_set_csv()
                        
        except Exception as e:
            # 파일 선택 창을 그냥 닫는 경우
            self.txt_Convert_path.setText("")
            return
    
    # csv 원상복귀(2017 버전으로)
    def list_set_csv(self):
        self.lisw_Convert_file.setRowCount(0)
        try:
            for row in (select_file):
                counts = self.lisw_Convert_file.rowCount()
                self.lisw_Convert_file.insertRow(counts)
                self.lisw_Convert_file.setItem(counts, 0, QTableWidgetItem(row))
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))
    
    # 2018-10-31
    # 잠조할 SHP 파일 입력 받음.
    def input_Ref_SHP(self):
        dir = os.path.dirname(sys.argv[0])
        try:
            global select_SHP
            select_SHP = QFileDialog.getOpenFileName(self, "Select Shape file", dir, '*.shp *.SHP')
            self.txt_inputSHP.setText(str(select_SHP))
            
        except Exception as e:
            self.txt_inputSHP.setText("")
            return
    
    # 입력받은 SHP 파일의 QGIS MAP 좌표를 받아야 함.
    def Ref_SHP_getcoord(self, txt):
        try:
            Vlayer = QgsVectorLayer(select_SHP, "SHP", "ogr")
            vlyrCRS = Vlayer.crs().authid()
            features = Vlayer.getFeatures()
            prov = Vlayer.dataProvider()
            
            global convert_crs
            convert_crs = []
            for raster in _ASC_filename:
                Rlyrcrs = QgsRasterLayer(raster).crs().authid()
                crsSrc = QgsCoordinateReferenceSystem(vlyrCRS)
                crsDest = QgsCoordinateReferenceSystem(Rlyrcrs)
#                 QgsMessageLog.logMessage("raster crs :  "+str(vlyrCRS)+" vector crs : "+str(Rlyrcrs),"GPM SHP")
                xform = QgsCoordinateTransform(crsSrc, crsDest)
                
                for feat in features:
                    feat2 = [str(feat_item).upper() for feat_item in feat.attributes()]  # 여기서 사용자가 이제 철자를 완전 동일하지 않아도 모두 대문자화 시킴
#                     if (txt) in  (feat.attributes()):
                    if (txt.upper()) in feat2:
                        geom = feat.geometry()
                        convert_crs_coord = (xform.transform(geom.asPoint()))
                        convert_crs.append(str(convert_crs_coord))
                    else:
                        pass
#             QgsMessageLog.logMessage(str(len(convert_crs)),"GPM SHP")
                    
            return (convert_crs)
                        
        except Exception as e:
            QgsMessageLog.logMessage(str(e), "GPM SHP")
        
    # 변경 된 CSV 변환 이벤트로 적용 2018-10-31
    def Convert_CSV_time(self):
        # lisw_Convert_file 리스트 초기화
        self.lisw_Convert_file.setRowCount(0)
        try:
            opencsv = open(select_file, 'r')
            reader_csv = csv.reader(opencsv)
#             try:
            headercsv = opencsv.readline().encode('utf-8')
#             except: 
#                 headercsv = opencsv.readline().decode('cp949').encode('utf-8') 
                
#             QgsMessageLog.logMessage(str(headercsv),"GPM SHP")
            # 헤더 지역별로 배열생성
            AreaName = headercsv.split(',')
            
            AreaCoord = []
            try:
                for name in AreaName[1:]:
                    AreaCoord.append(self.Ref_SHP_getcoord(name.replace("\n", "")))
            except:
                return "FIELDNAME ERROR"
            
#             QgsMessageLog.logMessage(str(AreaCoord),"GPM AreaCoord")
                
            i = 1
            global _CSV_filename
            del _CSV_filename[:]
            for row in (reader_csv):
                getfile = _util.GetFilename(str(row[0]))
                create_csv = open(select_file_path + "/{0}.csv".format(getfile), 'w+')
                self.CSV_filepath = []
                self.CSV_filepath.append(select_file_path + "/{0}.csv".format(getfile))
                
                counts = self.lisw_Convert_file.rowCount()
                
                self.lisw_Convert_file.insertRow(counts)
                self.lisw_Convert_file.setItem(counts, 0, QTableWidgetItem(select_file_path + "/{0}.csv".format(getfile)))
                
                global _CSV_filename
                
                _CSV_filename.append(select_file_path + "/{0}.csv".format(getfile))
                
                j = 0
                for cols in row[i:]:
                    # 여기서... 값이 없는 것은 제외하고 출력함
                    if cols.strip() != "":
                        if (AreaCoord[j]) != []:
                            value = str(AreaCoord[j]).replace("['(", "").replace(")']", "") + "," + cols + "\n"
#                         QgsMessageLog.logMessage(str(value),"GPM CSV")
                        create_csv.write(str(value))
                    j = j + 1
                       
            create_csv.close()
            opencsv.close()
            _util.MessageboxShowInfo("Info", "Complete convert file")
#             QgsMessageLog.logMessage(str(_CSV_filename),"GPM CSV") #OK 리스트 확인
            # txt_Convert_path 텍스트 값 초기화
            self.txt_Convert_path.clear()        
            
        except Exception as e:
            _util.MessageboxShowError("GPM CSV", str(e))
# #             AreaCoord.append(_coord.coordinate_dict(i.replace("\n","")))
    
#     # CSV 파일 변환 이벤트 _old
#     def Convert_CSV_event(self):
#         #lisw_Convert_file 리스트 초기화
#         self.lisw_Convert_file.setRowCount(0)
#         opencsv = open(select_file, 'r')
#         reader_csv = csv.reader(opencsv)
#         '''
#         #5/11 참고참고::
#                     뭐랄까 코드가 이동하면서 한글이 깨지는 것 같음... 문제가 되는 부분이 있다면 좌표값으로 변환할 때 매우 크게 문제가 되고 있어용.. 전부 1,1 이렇게 되니까..
#         '''
#         # 헤더 지역 받아옴
#         headercsv = opencsv.readline().decode('cp949').encode('utf-8')
#         # 헤더 지역별로 배열생성
#         AreaName = headercsv.split(',')
#         AreaCoord = []
#         for i in AreaName[1:]:
#             print
#             #AreaCoord.append(self.coordinate_dict(i))
#             '''
#             5/21 jo :
#             #마지막 값이 1,1 로 출력되는 오류 찾음
#             #원인은 위치 마지막 키 값에 \n 이 들어 있어서 except 문을 타고 1,1로 출력된 것.
#             #해당 문제가 없도록 replace를 사용해서 해당 오류 해결하였음.
#             '''
#             AreaCoord.append(_coord.coordinate_dict(i.replace("\n","")))
#         i = 1
#         #self.CSV_filepath = []#여기에 썼더니 값은 2개 들어오는데 리스트엔 3개가 뜨는 매직..!?
#         global _CSV_filename
#         del _CSV_filename[:]
#         for row in (reader_csv):
#             #2018-10-26 이 부분에서 오작동이 있던 것인데 파일 명만 받도록 변경하였음.
#             #포맷이 주신 샘플로 고정이 되어야 함. 아니면 다시 오류 발생 가능성이 아주 높음
#             getfile = _util.GetFilename(str(row[0]))
#             # 파일 생성 코드..
#             # 위치는 선택한 csv 파일과 같은 경로에 생성됨
#             create_csv = open(select_file_path + "/{0}.csv".format(getfile), 'w+')
#             # 흠 리스트로 받아서 처리 하려 했건만 잘안됨 나중에 확인..하나씩만 들어오는..
#             self.CSV_filepath = []
#             self.CSV_filepath.append(select_file_path + "/{0}.csv".format(getfile))
#             # 2018 -06-11 
#             counts = self.lisw_Convert_file.rowCount()
#             self.lisw_Convert_file.insertRow(counts)
#             self.lisw_Convert_file.setItem(counts, 0, QTableWidgetItem(select_file_path + "/{0}.csv".format(getfile)))
#             global _CSV_filename
#             _CSV_filename.append(select_file_path + "/{0}.csv".format(getfile))
#             
#             j = 0
#             for cols in row[i:]:
#                 value = AreaCoord[j] + "," + cols + "\n"
#                 j += 1
#                 create_csv.write(value)
#                 
#         
#         create_csv.close()
#         opencsv.close()
#         # 변환완료되었음을 알림
#         _util.MessageboxShowInfo("Info", "Complete convert file")
#         # txt_Convert_path 텍스트 값 초기화
#         self.txt_Convert_path.clear()
#     #    self.closewindow()
    
    # 기존의 기능으로 원복(이름으로 매칭... 일단 이 방법)
    def Apply_all_correction(self):
#         if len(_ASC_filename) != len(select_file):
        # 위성 격자와 지상 관측 데이터의 수가 일치해야 함.
        if len(_ASC_filename) != len(_CSV_filename):
            _util.MessageboxShowInfo("GPM NOTICE", "Number of CSV FILES and ASC FILES do not match.")
#             QgsMessageLog.logMessage("Number of CSV FILES and ASC FILES do not match.","GPM NOTICE")
            return
        
        # 보정 결과가 출력될 폴더 경로를 지정해야 함.
        if self.txtOutputDataPath.text().strip() == "":
            _util.MessageboxShowInfo("GPM NOTICE", " NOT set Output Path.")
            return
        
        # 시간 로그 측정.
        start_time_GPM = time.time()
        
        try:
            self.satellite_progressBar.setValue(0)
            self.satellite_progressBar.setMaximum(len(_ASC_filename))
            self.decimalChanged()
#             run_correction = _corr.run_correction(output_folder, _ASC_filename, select_file, _decimal)
#             run_correction = _corr.run_correction(output_folder, _ASC_filename, _CSV_filename, _decimal)
            QgsMessageLog.logMessage("decimal : " + str(_decimal) + " \n" + str(_ASC_filename) + "\n" + str(_CSV_filename) + "\n" + self.txtOutputDataPath.text() + "\n", "GPM APPLY ALL")
            
            # 연세대 보정 알고리즘 코드로 진입
            run_correction = _corr.run_correction(self.txtOutputDataPath.text(), (_ASC_filename), (_CSV_filename), _decimal)
            
            # 보정 시 측정 시간
            QgsMessageLog.logMessage("corr 1 : " + "%s" % (time.time() - start_time_GPM), "GPM Satellite")
            
            # 메시지 박스 외 Qgs 패널에서 확인 가능
#             QgsMessageLog.logMessage(str(run_correction),"GPM sate")
            
            # 보정 처리된 위성 격자에 prj 파일을 복사해옴.(위성격자 원본 데이터와 같은 좌표계)            
            dirpath = os.path.split(_ASC_filename[0])[0]
            self.Find_ASC_CRS(dirpath)
#             for count in range(len(select_file)):
            count = 0
            for count in range(len(_CSV_filename)):
                if self.chk_AddLayer.isChecked():
#                     QgsMessageLog.logMessage(self.txtOutputDataPath.text() + "/" + (os.path.split(os.path.splitext(_ASC_filename[count])[0])[1])+
#                                              ("_satellite_correction.asc"),"GPM _CSVFILENAME")
                    self.Addlayer_OutputFile(
                        self.txtOutputDataPath.text() + "/" + (os.path.split(os.path.splitext(_ASC_filename[count])[0])[1]) + ("_satellite_correction.asc"))
#                             os.path.basename(_CSV_filename[count]).split(".")[0]) + ".asc")
#                         output_folder + "\\" + (os.path.basename(_ASC_filename[count]).split(".")[0]) + "_" + (
#                             os.path.basename(select_file[count]).split(".")[0]) + ".asc")
                self.satellite_progressBar.setValue(count)
                count = count + 1
            QgsMessageLog.logMessage("QGIS LOAD: " + "%s" % (time.time() - start_time_GPM), "GPM Satellite")
            # prj 파일 복사 넣기
            
#             QgsMessageLog.logMessage(str(count),"GPM _CSV COUNT")
            # 그럼 여기서 새로 리스트 만들어서 넣음..
            self.Tree_Result.clear()
            self.Tree_Result.setHeaderLabels(["Apply List"])
            i = 0
            for ASC in range(len(_ASC_filename)):
                root = QtGui.QTreeWidgetItem(self.Tree_Result, [_ASC_filename[ASC]])
                value = _ASC_filename[i]
                SS = QtGui.QTreeWidgetItem(root, [value.replace(".asc", "_satellite_correction.asc")])
                ascFileName = _util.GetFilename(value)
#                 new_path = self.txtOutputDataPath.text()+"/"+str(ascFileName)+".png"
#                 QgsMessageLog.logMessage(str(new_path),"GPM SATE_PNG")
                
#                 # png 만들기
                if self.chk_makePng.isChecked():
                    new_path = self.txtOutputDataPath.text() + "/" + str(ascFileName) + "_satellite_correction.png"
#                     QgsMessageLog.logMessage(str(new_path),"GPM SATE_PNG")
                    SS = QtGui.QTreeWidgetItem(root, [new_path])
                    _PNG_filename.append(new_path)
                    png_path = new_path
                    # 이미지 생성
                    self.make_png(_ASC_filename[ASC], png_path)
                    
                self.satellite_progressBar.setValue(count + i)
                i = i + 1
            QgsMessageLog.logMessage("Make PNG : " + "%s" % (time.time() - start_time_GPM), "GPM Satellite")
#             QgsMessageLog.logMessage(str(i),"GPM _asc COUNT")
            
            # 기능이 모두 끝나면 메시지 알림
            _util.MessageboxShowInfo("GPM", str(run_correction))
            # 개발자용 확인용, 배포시 제거 바람.
#             create_filename = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_sate.txt"
#             create_file = open(create_filename,'w+')
#             create_file.write(run_correction)
#             create_file.close()

#                     SS = QtGui.QTreeWidgetItem(root, [value.replace("asc","png")])
#                     _PNG_filename.append(value.replace("asc","png"))
#                     png_path=value.replace("asc","png")
#                     # 이미지 생성
#                     self.make_png(_ASC_filename[ASC],png_path)

        except Exception as es:
            QMessageBox.information(None, "error", str(es))
    
    # 2018-11-02 신설 JO
    # 입력한 ASC의 prj 파일으르 복사해서 주려고 함.
    def Find_ASC_CRS(self, dirpath):
        # 입력된 asc 파일의 목록을 읽고 해당 파일의 파일명과 일치하는 prj를 결과폴더로 이동
        find_prj_list = []
        for (path, dir, files) in os.walk(dirpath):
            for filename in files:
                ext = os.path.splitext(filename)[-1]
                if ext == '.prj':
                    find_prj_list.append(("%s/%s" % (path, filename)))
        
        # 얻은 거 복사
        for prj in find_prj_list:
            fileprj = os.path.split(prj)[1]
            for aaa in _ASC_filename:
                if os.path.splitext(fileprj)[0] == os.path.split(os.path.splitext(aaa)[0])[1]:
                    shutil.copy(prj, self.txtOutputDataPath.text() + "/" + (fileprj).replace(".prj", "_satellite_correction.prj"))
    
    # 모든 리스트가 적용 되었을때 파일 목록으로 정
    def Apply_AllList_event(self):
        global _decimal, _PNG_filename
        # CSV 파일과 ASC 파일의 갯수가 같지 않으면 오류 메시지 출력
        if len(_CSV_filename) != len(_ASC_filename):
            QgsMessageLog.logMessage("Number of CSV FILES and ASC FILES do not match.", "GPM NOTICE")
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

            # 그럼 여기서 새로 리스트 만들어서 넣음..
            self.Tree_Result.clear()
            self.Tree_Result.setHeaderLabels(["Apply List"])
            i = 0
            for ASC in range(len(_ASC_filename)):
                root = QtGui.QTreeWidgetItem(self.Tree_Result, [_ASC_filename[ASC]])
                value = _CSV_filename[i]
                SS = QtGui.QTreeWidgetItem(root, [value])
                if self.chk_makePng.isChecked():
                    SS = QtGui.QTreeWidgetItem(root, [value.replace("csv", "png")])
                    _PNG_filename.append(value.replace("csv", "png"))
                    png_path = value.replace("csv", "png")
                    # 이미지 생성
                    self.make_png(_ASC_filename[ASC], png_path)
                i = i + 1

        except Exception as es:
            QMessageBox.information(None, "error", str(es))

    # 폼 화면 종료(닫기)
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

    # output 경로 받기
    def Output_path_Dialog(self):
         global output_folder
         output_folder = ""
         # output_path = select_file_path
         output_path = os.path.dirname(sys.argv[0])
         # asc 선택과 달리 폴더 지정
         output_folder = (QFileDialog.getExistingDirectory(self, "Select Output Directory", output_path))
         
         # 선택 폴더가 있다면
         if output_folder != "":
            output_folder = output_folder.replace("\\", "/")
            self.txtOutputDataPath.setText(output_folder)
         # 선택 폴더가 없다면
         else:
             self.txtOutputDataPath.setText("")

    # ok 버튼 누르면 실행 되는 부분임
    def run_Result(self):
        global _decimal
        count = 0
        save_path = output_folder

        progress = QProgressBar()  # progress bar 공통 부분1
        progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # progress bar 공통 부분2

        self.decimalChanged()
#         start_time = time.time()
        run_correction = _corr.run_correction(save_path, _ASC_filename, (self.CSV_filename), _decimal)

        # 종료시간
#         print ("--- %s seconds ---" %(time.time() - start_time))

        for count in range(len(self.CSV_filename)):
            if self.chk_AddLayer.isChecked() :
                self.Addlayer_OutputFile(save_path + "\\" + (os.path.basename(_ASC_filename[count]).split(".")[0]) + "_" + (os.path.basename(self.CSV_filename[count]).split(".")[0]) + ".asc")

            count = count + 1
            # 진행률 바 생성
            progressMessageBar = GPM._iface.messageBar().createMessage(("Progress rate"))
            progressMessageBar.layout().addWidget(progress)
            GPM._iface.messageBar().pushWidget(progressMessageBar, GPM._iface.messageBar().SUCCESS)
            progress.setMaximum(len(_ASC_filename))
             
            # 진행률 % 표현
            progress.setValue(count)
 
        _util.MessageboxShowInfo("Process Information", "performed {0} files. \n{1}".format(len(_ASC_filename), str(run_correction)))

        # 진행률 바가 100%가 되면 자동으로 메세지 바 삭제
        GPM._iface.messageBar().clearWidgets()
    
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
    def make_png(self, asc_path, png_path):
        color_path = os.path.dirname(os.path.realpath(__file__)) + "/Color/color.txt"
#         arg = "gdaldem.exe color-relief " + asc_path + " " + color_path + " " + png_path
        # v0.0.14 수정해보았음.
        mycall = [osgeo4w,
                 "gdaldem.exe",
                 "color-relief",
                 asc_path,
                 color_path,
                 png_path]
        callvalue = sub.call(mycall, shell=True)
        if callvalue != 0:
            _util.MessageboxShowInfo("Notice", "Not completed.")
    
    # 휴가 후 반영 ===============================================================
    
    # 배경 shp 관련 -- 이제 안씀.ㅎㅎㅎㅎ
#     def base_shp(self):
# #         sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+'/shp_tmp')
#         # 기본 값 임의 설정.
# #         self.shp_layer = "C:/Users/USER/.qgis2/python/plugins/GPM/shp_tmp/polyline.shp"
#         self.shp_layer = ""
#         self.txt_pngshp.setText(self.shp_layer)
#         base_shp = QgsVectorLayer(self.shp_layer, (os.path.basename(self.shp_layer)).split(".shp")[0], "ogr")
# #         QgsMapLayerRegistry.instance().addMapLayers([self.layer, base_map], False)
#         QgsMapLayerRegistry.instance().addMapLayer(base_shp, False)
#         self.gpm_canvas.setExtent(base_shp.extent())
#         self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(base_shp)])
     
    # 1. polgin(유역도) shape file 선택 함수 
    def btn_baseShp_polygon(self):
        self.shp_layer_polygon = ""
        dir = os.path.dirname(sys.argv[0])
#         global select_SHP

        try:
            self.shp_layer_polygon = QFileDialog.getOpenFileName(self, "Select Shape file", dir, '*.shp *.SHP')
            # 파일을 선택했다면~
            if self.shp_layer_polygon != "":
                self.txt_pngshp_polygon.setText(self.shp_layer_polygon)
                basepolygon = QgsVectorLayer(self.shp_layer_polygon, (os.path.basename(self.shp_layer_polygon)).split(".shp")[0], "ogr")
    #         QgsMapLayerRegistry.instance().addMapLayers([self.layer, base_map], False)
                QgsMapLayerRegistry.instance().addMapLayer(basepolygon, False)
#                 self.gpm_canvas.setExtent(basepolygon.extent())
#                 self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(basepolygon)])
                self.gpm_canvas.zoomToFullExtent()
#                 self.gpm_canvas.setExtent(base_shp.extent())
#                 self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(base_shp)])
            # 파일 선택을 안해서 여전히 빈 값이면~
            else:
#                 _util.MessageboxShowInfo("GPM","No selected shape file.")
                self.shp_layer_polygon = ""
                self.txt_pngshp_polygon.setText("")
                return
             
        except Exception as e:
            self.txt_pngshp_polygon.setText("")
            return
        
    # 2. line(하천망도) shape file 선택 함수
    def btn_baseShp_line(self):
        self.shp_layer_line = ""
        dir = os.path.dirname(sys.argv[0])
#         global select_SHP

        try:
            self.shp_layer_line = QFileDialog.getOpenFileName(self, "Select Shape file", dir, '*.shp *.SHP')
            # 파일을 선택했다면~
            if self.shp_layer_line != "":
                self.txt_pngshp_line.setText(self.shp_layer_line)
                baseLine = QgsVectorLayer(self.shp_layer_line, (os.path.basename(self.shp_layer_line)).split(".shp")[0], "ogr")
    #         QgsMapLayerRegistry.instance().addMapLayers([self.layer, base_map], False)
                QgsMapLayerRegistry.instance().addMapLayer(baseLine, False)
#                 self.gpm_canvas.setExtent(baseLine.extent())
#                 self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLine)])
                self.gpm_canvas.zoomToFullExtent()
#                 self.gpm_canvas.setExtent(base_shp.extent())
#                 self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(base_shp)])
            # 파일 선택을 안해서 여전히 빈 값이면~
            else:
#                 _util.MessageboxShowInfo("GPM","No selected shape file.")
                self.shp_layer_line = ""
                self.txt_pngshp_line.setText("")
                return
             
        except Exception as e:
            self.txt_pngshp_line.setText("")
            return
    
    # 3. point(관측소 위치) shape file 선택 함수
    def btn_baseShp_point(self):
        self.shp_layer_point = ""
        dir = os.path.dirname(sys.argv[0])
#         global select_SHP

        try:
            self.shp_layer_point = QFileDialog.getOpenFileName(self, "Select Shape file", dir, '*.shp *.SHP')
            # 파일을 선택했다면~
            if self.shp_layer_point != "":
                self.txt_pngshp_point.setText(self.shp_layer_point)
                basePoint = QgsVectorLayer(self.shp_layer_point, (os.path.basename(self.shp_layer_point)).split(".shp")[0], "ogr")
    #         QgsMapLayerRegistry.instance().addMapLayers([self.layer, base_map], False)
                QgsMapLayerRegistry.instance().addMapLayer(basePoint, False)
#                 self.gpm_canvas.setExtent(basePoint.extent())
#                 self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(basePoint)])
                self.gpm_canvas.zoomToFullExtent()
            # 파일 선택을 안해서 여전히 빈 값이면~
            else:
                self.shp_layer_point = ""
#                 _util.MessageboxShowInfo("GPM","No selected shape file.")
                self.txt_pngshp_point.setText("")
                return
             
        except Exception as e:
            self.txt_pngshp_point.setText("")
            return
     
    # 원래는 따로 분리했었는데...  기회가 되면 다시 분리할 것
    def savePng_base(self, canvas, raster, polygon, line, point, saveName):
#     def savePng_base(self,canvas,raster,polygon, saveName):
        try:
             #여기가 지금 주먹구구식인데 나중에 다시 관리
            self.rasterLayer = QgsRasterLayer(raster, ((os.path.basename(raster)).split(".png")[0]), "gdal")
                        
            #SHP 3개
            if polygon != "" and line != "" and point != "":
                QgsMessageLog.logMessage(str(polygon) + " " + str(line) + " " + str(point), "GPM IMG")
                baseLayer_point = QgsVectorLayer(point, (os.path.basename(point)).split(".shp")[0], "ogr")
                baseLayer_line = QgsVectorLayer(line, (os.path.basename(line)).split(".shp")[0], "ogr")
                baseLayer_polygon = QgsVectorLayer(polygon, (os.path.basename(polygon)).split(".shp")[0], "ogr")
                QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer, baseLayer_polygon, baseLayer_line, baseLayer_point], False)
                list_layer = [baseLayer_line, baseLayer_point, baseLayer_polygon, self.rasterLayer]  # base layer가 위에
                self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_polygon),QgsMapCanvasLayer(baseLayer_line),QgsMapCanvasLayer(baseLayer_point),QgsMapCanvasLayer(self.rasterLayer)])
                self.gpm_canvas.zoomToFullExtent()
                
            #SHP 1개 - Polygon만
            if polygon != "" and line == "" and point == "":
                QgsMessageLog.logMessage(str(polygon) + " " + str(line) + " " + str(point), "GPM IMG")
                baseLayer_polygon = QgsVectorLayer(polygon, (os.path.basename(polygon)).split(".shp")[0], "ogr")
                QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer, baseLayer_polygon], False)
                list_layer = [baseLayer_polygon, self.rasterLayer]  # base layer가 위에
                self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_polygon),QgsMapCanvasLayer(self.rasterLayer)])
                self.gpm_canvas.zoomToFullExtent()
            
            #SHP 1개 - Line 만    
            if polygon == "" and line != "" and point == "":
                QgsMessageLog.logMessage(str(polygon) + " " + str(line) + " " + str(point), "GPM IMG")
                baseLayer_line = QgsVectorLayer(line, (os.path.basename(line)).split(".shp")[0], "ogr")
                QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer, baseLayer_line], False)
                list_layer = [baseLayer_line, self.rasterLayer]  # base layer가 위에
                self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_line),QgsMapCanvasLayer(self.rasterLayer)])
                self.gpm_canvas.zoomToFullExtent()
            
            #SHP 1개 - Point만    
            if polygon == "" and line == "" and point != "":
                QgsMessageLog.logMessage(str(polygon) + " " + str(line) + " " + str(point), "GPM IMG")
                baseLayer_point = QgsVectorLayer(point, (os.path.basename(point)).split(".shp")[0], "ogr")
                QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer, baseLayer_point], False)
                list_layer = [baseLayer_point, self.rasterLayer]  # base layer가 위에
                self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_point),QgsMapCanvasLayer(self.rasterLayer)])
                self.gpm_canvas.zoomToFullExtent()
                
            #SHP 2개 - polygon, line
            if polygon !="" and line !="" and point =="":
                baseLayer_polygon = QgsVectorLayer(polygon,(os.path.basename(polygon)).split(".shp")[0],"ogr")
                baseLayer_line = QgsVectorLayer(line, (os.path.basename(line)).split(".shp")[0], "ogr")
                QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer,baseLayer_polygon, baseLayer_line], False)
                list_layer = [baseLayer_line,baseLayer_polygon, self.rasterLayer]  # base layer가 위에
                self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_polygon),QgsMapCanvasLayer(baseLayer_line),QgsMapCanvasLayer(self.rasterLayer)])
                self.gpm_canvas.zoomToFullExtent()
            
            #SHP 2개 -  line, point
            if polygon =="" and line !="" and point !="":
                baseLayer_point = QgsVectorLayer(point, (os.path.basename(point)).split(".shp")[0], "ogr")
                baseLayer_line = QgsVectorLayer(line, (os.path.basename(line)).split(".shp")[0], "ogr")
                QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer, baseLayer_line,baseLayer_point], False)
                list_layer = [baseLayer_point,baseLayer_line, self.rasterLayer]  # base layer가 위에
                self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_point),QgsMapCanvasLayer(baseLayer_line),QgsMapCanvasLayer(self.rasterLayer)])
                self.gpm_canvas.zoomToFullExtent()
            
            #SHP 2개 - polygon, point
            if polygon !="" and line =="" and point !="":
                baseLayer_polygon = QgsVectorLayer(polygon,(os.path.basename(polygon)).split(".shp")[0],"ogr")
                baseLayer_point = QgsVectorLayer(point, (os.path.basename(point)).split(".shp")[0], "ogr")
                QgsMapLayerRegistry.instance().addMapLayers([self.rasterLayer,baseLayer_polygon, baseLayer_point], False)
                list_layer = [baseLayer_point,baseLayer_polygon, self.rasterLayer]  # base layer가 위에
                self.gpm_canvas.setLayerSet([QgsMapCanvasLayer(baseLayer_polygon),QgsMapCanvasLayer(baseLayer_point),QgsMapCanvasLayer(self.rasterLayer)])
                self.gpm_canvas.zoomToFullExtent()
                 
            layers = [layer.id() for layer in list_layer]
            self.saveAScanvas(layers, saveName)

        
        except Exception as exc:
            QgsMapLayerRegistry.instance().removeMapLayers(layers)
            _util.MessageboxShowError("GPM IMG", str(exc))
            return
    
    # Canvas Zoom Full 
    def canvas_zoomFull(self):
        self.gpm_canvas.refresh()
        self.gpm_canvas.zoomToFullExtent()
        self.gpm_canvas.refresh()
        self.gpm_canvas.zoomToFullExtent()
        
    def saveAScanvas(self, layers, saveName):
        # 이 부분은 이미지 사이즈임... 나중에 래스터와 동일한 사이즈로 만들어주세요! 라고 하면 그 때 래스터 사이즈 get 하는 거 알아내서 하도록...
        # 조금 귀찮아서..
        width = 800
        height = 600
         
        dpi = 92
        img = QImage(QSize(width, height), QImage.Format_RGB32)
        img.setDotsPerMeterX(dpi / 25.4 * 1000)
        img.setDotsPerMeterY(dpi / 25.4 * 1000)
        
        self.canvas_zoomFull()
        extent = self.gpm_canvas.extent()
        self.canvas_zoomFull()
#             self.canvas_zoomFull()
          
        mapSettings = QgsMapSettings()
        mapSettings.setMapUnits(0)
        mapSettings.setExtent(extent)
        mapSettings.setOutputDpi(dpi)
        mapSettings.setOutputSize(QSize(width, height))
        mapSettings.setLayers(layers)
        mapSettings.setFlags(QgsMapSettings.Antialiasing | QgsMapSettings.UseAdvancedEffects
                             | QgsMapSettings.ForceVectorOutput | QgsMapSettings.DrawLabeling)
          
        p = QPainter()
        p.begin(img)
        mapRender = QgsMapRendererCustomPainterJob(mapSettings, p)
        mapRender.start()
        mapRender.waitForFinished()
        p.end()
          
#         saveName = "D:/Working/Gungiyeon/GPM/GPM_test/T20181213/test.png"
        img.save(saveName, 'png')
        QgsMapLayerRegistry.instance().removeMapLayers(layers)
    
    def Folder_List(self, type):
        try:
             folderpath = QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', '', QtGui.QFileDialog.ShowDirsOnly)
             filelsit = self.search(folderpath)
             self.SettingListWidget(filelsit, type)
        except Exception as e:
            _util.MessageboxShowError("GPM", str(e))
    
    def SettingListWidget(self, filelsit, type):

        if type == "ASC":
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

    def search(self, dirname):
        fileList = []
        if dirname != "" and dirname is not None:
            filenames = os.listdir(dirname)
            for filename in filenames:
                filePath = os.path.join(dirname, filename)
                fileList.append(filePath)
        return fileList

    # 사용자가 ASC 파일이 포함된 폴더를 선택하고 직접 PNG 파일로 변환 하는 함수
    def Make_png_menu(self):
        try:
            self.btl_png_list.clear()  # 수행시 초기화 v0.0.14 추가
            items = self.tbl_asc_list.selectedItems()
            
            canvas = self.gpm_canvas; 
            
            try:
                # vector layer가 전부 있어야 작동하게 할거야 귀찮아
#                 if vectorLayer_polygon !="" and vectorLayer_line !="" and vectorLayer_point !="":
                if len(items) > 0:
                    for i in list(items):
                        # 2018-10-25 v0.0.14 추가
                        asc_file = _util.GetFilename(i.text())
                        png_name = self.txt_output_png.text() + "/" + asc_file.upper() + ".PNG"
                        sleep(0.5)
                        
                        self.make_png(i.text(), png_name)
                        
                        try:
#                             if self.shp_layer_polygon !="" :
#                             QgsMessageLog.logMessage("1","GPM IMG")
#                                 vectorLayer_polygon =self.shp_layer_polygon;
                        # 여기에 분기
                            # base img 있는 png 추가 생성
        #                     layers = [layer.id() for layer in self.gpm_canvas.legendInterface().layers()]
#                             savePath = (png_name.upper()).replace(".PNG", "_base.png") #2019-03-14 쓰지 않아
#                             QgsMessageLog.logMessage("2","GPM IMG")
        #                     QgsMessageLog.logMessage(str(savePath),"GPM IMG")
        #                     QgsMapLayerRegistry.instance().addMapLayers([png_name,self.baseLayer], False)
#                                 saveImg = self.savePng_base((self.gpm_canvas), (png_name), (self.shp_layer_polygon), savePath)
#                             saveImg = self.savePng_base(self.gpm_canvas, png_name, self.shp_layer_polygon,self.shp_layer_line,self.shp_layer_point, savePath)
                            saveImg = self.savePng_base(self.gpm_canvas, png_name, self.shp_layer_polygon, self.shp_layer_line, self.shp_layer_point, png_name)
                            QgsMessageLog.logMessage("6", "GPM IMG")
                            
                            sleep(0.5)
                            self.btl_png_list.addItem(png_name)
                            
#                             saveImg = self.savePng_base(self.gpm_canvas, png_name, vectorLayer_polygon,vectorLayer_line,vectorLayer_point, savePath)
                        except:
                            sleep(0.5)
                            self.btl_png_list.addItem(png_name)  # 이게 결과 png 파일임. 이것만 들어가도록 처리..
    #                     self.btl_png_list.addItem(i.text().upper().replace(".ASC",".PNG"))
                        # self.Png_Add_Text(i.text().upper().replace(".ASC",".PNG"))
                    self.shp_layer_polygon = "" ;self.shp_layer_line = "";self.shp_layer_point = ""
                    self.txt_pngshp_polygon.setText("");self.txt_pngshp_line.setText("");self.txt_pngshp_point.setText("")
                else:
                    _util.MessageboxShowError("GPM", "No ASC file selected.")
                    return
#                 else:
#                         _util.MessageboxShowError("GPM","Not selected shape file.")
#                         return
            except Exception as exc:
                _util.MessageboxShowError("GPM", str(exc))
                return
        except Exception as exc:
            _util.MessageboxShowError("GPM", str(exc))
            return

    def Make_gif_user(self):
        try:
            if self.txt_save_gif_path_imag.text() == "":
                _util.MessageboxShowError("GPM", "The file path is not set.")
                self.txt_save_gif_path_imag.setFocus()
                return

            # 이미지 목록 리스트
            img_list = []
            items = self.btl_png_list.selectedItems()
            if len(items) > 0:
                for file in (items):
                    self.Png_Add_Text(str(file.text()))
                    sleep(0.5)
                    img_list.append(imageio.imread(file.text()))
                    
                sleep(1)
                imageio.mimsave(self.txt_save_gif_path_imag.text(), img_list, duration=(self.Interval_box_imag.value()))
                
            else:
                _util.MessageboxShowError("Notice", "No PNG file selected.")
                return
            QMessageBox.information(None, "Notice", "Make GIF")
        except Exception as ex:
            QMessageBox.Warning(None, "Notice", str(ex))

    def Png_Add_Text(self, filepath):
        try:
            # img = Image.open("C:/Users/hermesys/Desktop/Convert/2.png")
            # draw = ImageDraw.Draw(img)
            # font = ImageFont.truetype("sans-serif.ttf", 20)
            # draw.text((0, 0),"test",(255,255,255),font=font)
            # img.save("C:/Users/hermesys/Desktop/Convert/2.png")
            
            # 글자 사이즈 값은 나중에 조절 해야 할듯함
            im1 = Image.open(filepath)
            width, height = im1.size
            # 2018-10-26 요청에 따라 크기 줄임
            font_size = int(width / 50)
#             QgsMessageLog.logMessage(str(font_size)+" : "+str(height)+" : "+str(width),"GPM IMG")
            font = ImageFont.truetype("./arial.ttf", font_size)
            
            fileName = _util.GetFilename(filepath)
#             QgsMessageLog.logMessage(fileName.split("_")[0],"GPM IMG")
            # Drawing the text on the picture
            draw = ImageDraw.Draw(im1)
#             draw.text((0, 0),fileName,(255,0,128),font=font)
#             draw.text((0, 0),(fileName.split("_")[0]),(255,0,128),font=font)
            file_name_replace = str((fileName.split("_")[0]).split("-")[0:]).replace(", ", "-").replace("'", "")
            print file_name_replace
#             QgsMessageLog.logMessage(str(file_name_replace), "GPM PNG ADD")
#             draw.text((0, 0),file_name_replace,(255,255,0),font=font) #노란색 글씨
            draw.text((0, 0), file_name_replace, (255, 0, 0), font=font)  # 빨강
#             draw.text((0, 0),file_name_replace,(0,0,255),font=font) #파랑
            draw = ImageDraw.Draw(im1)
 
            # Save the image with a new name
            im1.save(filepath)
        except Exception as e:
            _util.MessageboxShowInfo("GPM", str(e))
    
    
    # ================== wget data download ===============
    def Rdo_Selected_wget(self):
        if self.rdo_64.isChecked() == True:
            self.userOS = "64bit"
        
#         if self.rdo_32.setChecked(True):
        if self.rdo_32.isChecked() == True:
            self.userOS = "32bit"
    
    def wget_save_path(self):
        global wget_folder
        wget_path = os.path.dirname(sys.argv[0])
        wget_folder = (QFileDialog.getExistingDirectory(self, "Select Output Directory", wget_path))
        self.txt_bat_path.setText(wget_folder)
    
    def wget_create_bat(self):
#         QgsMessageLog.logMessage(str(self.userOS),"WGET")
        try:
            self.wget_progress.setValue(0)
            
#             QgsMessageLog.logMessage(str(self.txt_userID.text())+"\n"+str(self.txt_userPW.text()),"GPM WGET")
            userId = self.txt_userID.text() ; userPw = self.txt_userPW.text()
            datadownlod = wget.wget_download(str(self.userOS), userId, userPw, self.start_date.text(), self.end_date.text(), wget_folder)
#             QgsMessageLog.logMessage(str(self.userOS),"WGET")
            
            count = 0
            for down in datadownlod:
                 
                count = (count + 1)
                self.wget_progress.setValue(count)
                sub.call(down, shell=True)  # 자동 수행 2019-03-12
             
            sleep(0.5)
            self.wget_progress.setMaximum(len(datadownlod))   
                
#                 os.system(down)
#                 QgsMessageLog.logMessage(str(down),"WGET")
#             os.system(datadownlod)
#             _util.MessageboxShowInfo("GPM", "A batch file was created on the desktop.")
            _util.MessageboxShowInfo("GPM", ("바탕화면에 GPM_data_download.bat 파일이 생성되었습니다.").decode('utf-8'))
        except Exception as e:
            _util.MessageboxShowError("GPM WGET", str(e))    
        
#     def wget_create_bat(self):
#         try:
# #             output = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_data_download.bat"
#             wgetFile= wget.create_bat_script(self.start_date.text(),self.end_date.text(),wget_folder)
#             _util.MessageboxShowInfo("GPM", "A batch file was created on the desktop.")
# #             for wget_count in (wgetFile):
# #                 stdout = sub.Popen(wget_count,stdout=sub.PIPE)
# #                 self.data_process_log.setText(str(stdout))
# #             for wget_count in range(len(wgetFile)):
# #                 self.data_process_log.setText(wgetFile[wget_count])
# #             output = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_data_download.txt"
# #             outputfile = open(output,'w+')
# #             for wget_count in (wgetFile):
# #                 wget_count = wget_count.replace("\\","/")
# #             stdoutput = os.popen2(wgetFile[0]).read()
# #             stdoutput = subprocess.call(wgetFile[0],stdout=subprocess.PIPE)
# #             outputstr=process.stdout.readline()
# #             outputfile.write(stdoutput)
# #             QgsMessageLog.logMessage(str(stdoutput),"GPM WGET READ")
# #                 for line in strprocess.stdout:
# #                 output= strprocess.communicate()
# 
#             
# #             outputfile.close()   
# #                 stdoutput=self.run_command(wget_count)
# #                 stdoutput = sub.check_output([wget_count],stderr=sub.STDOUT)
#                 
# #                 stdoutput = os.popen4(wget_count)[1].read()
# # #                 
# #                 for row in (open(output,'r').read()):
# #                     self.data_process_log.setText(row)
# #             
# #             file.close()
# #                 stdouterr = os.popen4(wget_count)[1].read()
# #                 stdouterr = sub.check_output(wget_count)
# #                 QgsMessageLog.logMessage(str(stdouterr),"GPM wget")
# #                 self.data_process_log.setText(stdouterr)
# #                 sleep(0.01)
# 
#             
# #             _util.MessageboxShowInfo("GPM", "A batch file was created on the desktop.")
# #             _util.MessageboxShowInfo("GPM", ("바탕화면에 GPM_data_download.bat 파일이 생성되었습니다.").decode('utf-8'))
#         except Exception as e:
#             _util.MessageboxShowError("GPM",str(e))
    
#     def run_command(self,command):
#         QgsMessageLog.logMessage(str(command),"GPM wget output")
#         process = Popen(command,stdout=PIPE,shell=True)
#         while True:
#             line = process.stdout.readline()
#             self.data_process_log.setText(str(line))
#             if not line:
#                 break
#             yield line
#         output,err = process.communicate()
    
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

