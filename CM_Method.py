# -*- coding: utf-8 -*-
"""
------------------
 CM 보정
 1. 지상 데이터 IDW 보간
 2. 위성 데이터 IDW 보간, 위성2 데이터 생성
 3. DIFF=위성2-지상IDW
 4. origin 위성-DIFF
------------------
"""
import os, subprocess

from qgis import processing
from qgis.core import (
    QgsRasterLayer,
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
    QgsVectorFileWriter,
)
from qgis.PyQt.QtWidgets import QTableWidgetItem
from osgeo import gdal, osr


class cm_method:
    def __init__(self, input_raster, dist, input_csv, output_path, tbl_Result_CM):
        self.table = tbl_Result_CM
        ra = QgsRasterLayer(input_raster, "gpm", "gdal")

        ra_gdal = gdal.Open(input_raster)
        colums = ra_gdal.RasterXSize
        rows = ra_gdal.RasterYSize

        # pixel size 추가, 2020-08-25
        gt = ra_gdal.GetGeoTransform()
        print(gt)
        pixelSizeX = gt[1]
        pixelSizeY = -gt[5]
        print(pixelSizeX)
        print(pixelSizeY)
        print(colums, rows)

        extent_layer_1 = str(ra.extent()).split(":")[1].split()
        # extent 범위 수정, 2020-08-25
        print(
            extent_layer_1[0],
            extent_layer_1[2],
            extent_layer_1[1].replace(",", ""),
            extent_layer_1[3].split(">")[0],
        )
        extent_layer = "{0},{1},{2},{3}".format(
            extent_layer_1[0],
            extent_layer_1[2],
            extent_layer_1[1].replace(",", ""),
            extent_layer_1[3].split(">")[0],
        )

        self.read_Layer_Get_info(input_raster)
        if os.path.splitext(input_csv)[1] == ".csv":
            input_csv = self.csv2shp_save(input_csv)
            ra2 = self.SAT_idw(
                dist,
                (extent_layer),
                self.point2raster(input_csv, input_raster, output_path),
                colums,
                rows,
                pixelSizeX,
                output_path,
            )
            ground = self.ground_idw(
                dist, (extent_layer), input_csv, colums, rows, pixelSizeX, output_path
            )
            Diff = self.calculator_diff(ra2, ground, output_path)
        #             self.calc_CMmethod(input_raster,Diff,output_path)
        else:
            #         ra2 = self.SAT_idw(dist,(ra.extent()),self.point2raster(input_csv,input_raster,output_path),colums,rows,output_path)
            ra2 = self.SAT_idw(
                dist,
                (extent_layer),
                self.point2raster(input_csv, input_raster, output_path),
                colums,
                rows,
                pixelSizeX,
                output_path,
            )
            # #         ra2 = self.SAT_idw(dist,(ra.extent()),input_sat,colums,rows)
            #         ground=self.ground_idw(dist,(ra.extent()),input_csv,colums,rows,output_path)
            ground = self.ground_idw(
                dist, (extent_layer), input_csv, colums, rows, pixelSizeX, output_path
            )

        Diff = self.calculator_diff(ra2, ground, output_path)
        self.calc_CMmethod(input_raster, Diff, output_path)

    # #지상데이터 IDW 보간 - CREATE GROUND_IDW
    def ground_idw(
        self,
        distance_coefficient,
        extent,
        interporation_data,
        column,
        row,
        pixelsize,
        output_path,
    ):
        print("GROUND_IDW")
        print(interporation_data)
        #         output = output_path+"/"+os.path.basename(interporation_data).split(".")[0]+"_ground_idw.asc"
        output = (
            output_path
            + "/"
            + (os.path.basename(os.path.splitext(interporation_data)[0]))
            + "_idw.tif"
        )

        #         output="D:/Working/KICT/2020/sample1/20200619/"+os.path.basename(interporation_data).split(".")[0]+"_idw.asc"
        if os.path.basename(interporation_data).split(".")[0] == "ground_point_sample":
            alg = {
                "DISTANCE_COEFFICIENT": distance_coefficient,
                "EXTENT": extent,
                "INTERPOLATION_DATA": interporation_data
                + "::~::0::~::1::~::0",  # 이 부분 변경해야 함.
                "OUTPUT": output,
                "COLUMNS": column,
                "ROWS": row,
                "PIXEL_SIZE": pixelsize,
            }
        else:
            alg = {
                "DISTANCE_COEFFICIENT": distance_coefficient,
                "EXTENT": extent,
                "INTERPOLATION_DATA": interporation_data
                + "::~::0::~::2::~::0",  # 이 부분 변경해야 함.
                "OUTPUT": output,
                "COLUMNS": column,
                "ROWS": row,
                "PIXEL_SIZE": pixelsize,
            }

        print(alg)
        processing.run("qgis:idwinterpolation", alg)
        self.convert2asc(output)
        return output

    # 위성 shp 생성
    def point2raster(self, input_shp, input_sat, output_path):
        print("POINT2RASTER")
        output = (
            output_path
            + "/"
            + (os.path.basename(os.path.splitext(input_sat)[0]))
            + "_RS.shp"
        )
        print(output)
        alg = {
            "COLUMN_PREFIX": "rvalue",
            "INPUT": input_shp,
            "OUTPUT": output,
            "RASTERCOPY": input_sat,
        }
        processing.run("qgis:rastersampling", alg)
        return output

    # 위성데티어 IDW 보간-CREATE SAT2
    def SAT_idw(
        self,
        distance_coefficient,
        extent,
        interporation_data,
        column,
        row,
        pixelsize,
        output_path,
    ):
        print("SAT_IDW")
        print(interporation_data)
        #         output = output_path+"/"+os.path.basename(interporation_data).split(".")[0]+"_idw.asc"
        output = (
            output_path
            + "/"
            + os.path.basename(interporation_data).split(".")[0]
            + "_idw.tif"
        )

        #         output="D:/Working/KICT/2020/sample1/20200619/"+os.path.basename(interporation_data).split(".")[0]+"_idw.asc"
        alg = {
            "DISTANCE_COEFFICIENT": distance_coefficient,
            "EXTENT": extent,
            "INTERPOLATION_DATA": interporation_data + "::~::0::~::3::~::0",
            "OUTPUT": output,
            "COLUMNS": column,
            "ROWS": row,
            "PIXEL_SIZE": pixelsize,
        }
        print(alg)

        processing.run("qgis:idwinterpolation", alg)
        self.convert2asc(output)
        return output

    # DIFF = SAT2-GROUND_IDW
    def calculator_diff(self, SAT2, ground_idw, output_path):
        print(SAT2)
        print(ground_idw)

        #         output=output_path+"/"+os.path.basename(SAT2).split('.')[0]+"_"+os.path.basename(ground_idw).split(".")[0]+"_DIFF.asc"
        output = (
            output_path
            + "/"
            + os.path.basename(SAT2).split(".")[0]
            + "_"
            + os.path.basename(ground_idw).split(".")[0]
            + "_DIFF.tif"
        )

        #         output="D:/Working/KICT/2020/sample1/20200619/"+os.path.basename(SAT2).split('.')[0]+"_"+os.path.basename(ground_idw).split(".")[0]+"_DIFF.asc"
        print(output)

        alg = 'gdal_calc --calc "A-B" --format GTiff --type Float32 -A "{0}" --A_band 1 -B "{1}" --B_band 1 --outfile "{2}" '.format(
            SAT2, ground_idw, output
        )
        print(alg)
        #         os.system(alg)
        subprocess.call(alg, shell=True)
        self.convert2asc(output)
        return output

    # SAT - DIFF
    def calc_CMmethod(self, SAT, DIFF, output_path):
        output = (
            output_path + "/" + (os.path.basename(os.path.splitext(SAT)[0])) + "_cm.tif"
        )
        alg = 'gdal_calc --calc "A-B" --format GTiff --type Float32 -A "{0}" --A_band 1 -B "{1}" --B_band 1 --outfile "{2}" --NoDataValue={3}  '.format(
            SAT, DIFF, output, self.Nodata
        )
        subprocess.call(alg, shell=True)
        self.convert2asc(output)

        counts = self.table.rowCount()
        self.table.insertRow(counts)
        self.table.setItem(counts, 0, QTableWidgetItem(output))
        return output

    # ground csv convert shapfile and save
    def csv2shp_save(self, csv):
        #         crs='EPSG:4326'
        crs = self.Projection
        input_csv = csv
        Output_Layer = (
            os.path.dirname(csv) + "/" + os.path.basename(csv).split(".csv")[0] + ".shp"
        )
        # field_1 field_2 = 좌표정보 인 csv
        uri = "file:///{0}?type=csv&useHeader=No&detectTypes=yes&xField=field_1&yField=field_2&crs={1}&spatialIndex=no&subsetIndex=no&watchFile=no".format(
            input_csv, crs
        )
        print(uri)
        crs_sys = QgsCoordinateReferenceSystem(crs)
        layer_csv = QgsVectorLayer(uri, os.path.basename(input_csv), "delimitedtext")
        QgsVectorFileWriter.writeAsVectorFormat(
            layer_csv,
            Output_Layer,
            "utf-8",
            driverName="ESRI Shapefile",
            destCRS=crs_sys,
        )
        return Output_Layer

    # raster 읽어서 nodata,projection get info
    def read_Layer_Get_info(self, ratserLayer):
        self.Nodata = ""
        self.Projection = ""
        tiff_ds = gdal.Open(ratserLayer)
        self.Nodata = str(tiff_ds.GetRasterBand(1).GetNoDataValue())
        print("nodata : ", self.Nodata)
        prj = tiff_ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        # self.Projection = str(srs.GetAttrValue('authority',0)+":"+srs.GetAttrValue('authority',1))
        # if self.Projection=""
        print("self.Projection  : " + str(self.Projection))

        # 2020-09-09 박: 좌표 정보 받는거 확인
        outputLayer = QgsRasterLayer(
            ratserLayer, ((os.path.basename(ratserLayer))), "gdal"
        )
        # layer = QgsRasterLayer()
        self.Projection = outputLayer.crs().authid()

    # 마지막 결과 데이터들 asc 로 포맷 변환
    def convert2asc(self, input_file):
        output = (
            os.path.dirname(input_file)
            + "/"
            + (os.path.basename(input_file).split(".tif")[0])
            + ".asc"
        )
        if os.path.exists(output) == False:
            arg = 'gdal_translate -of AAIGrid "{0}" "{1}" '.format(input_file, output)
            subprocess.call(arg, shell=True)
