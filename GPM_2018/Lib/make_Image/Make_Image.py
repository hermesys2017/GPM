# -*- coding: utf-8 -*-
'''
Created on 2019. 3. 8.

ASC 이미지 생성 소스 분리
@author: MH.JO
'''

import os,sys
import subprocess as sub

osgeo4w="c://Program Files/QGIS 2.18/OSGeo4W.bat"

#ASC TO PNG 코드
def make_png(asc_path, png_path):
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
    if callvalue != 0:
        return "Not Completed."
#         _util.MessageboxShowInfo("Notice", "Not completed.")

# ==== Load Shape Layer ====
def Load_shapeLayer():
    shape_layer = ""
    

# ==== Save As Canvas ====



# #유역도 폴리곤을 배경으로
# def base_polygon():
#     shp_polygon =""
# 
# #하천망도 라인을 배경으로
# def base_line():
#     shp_line=""
# 
# #관측소 위치를 배경으로
# def base_point():
#     shp_point=""

