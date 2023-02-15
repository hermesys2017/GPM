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
import sys, os, subprocess
from qgis import processing
from qgis.core import *
from osgeo import gdal


class cm_method_run:
    def __init__(self, input_raster, dist, input_csv):
        ra = QgsRasterLayer(input_raster, "gpm", "gdal")
        ra_gdal = gdal.Open(input_raster)
        colums = ra_gdal.RasterXSize
        rows = ra_gdal.RasterYSize
        ra2 = self.SAT_idw(
            dist,
            (ra.extent()),
            self.point2raster(input_csv, input_raster),
            colums,
            rows,
        )
        ground = self.ground_idw(dist, (ra.extent()), input_csv, colums, rows)
        Diff = self.calculator_diff(ra2, ground)
        self.calc_CMmethod(input_raster, Diff)

    # #지상데이터 IDW 보간 - CREATE GROUND_IDW
    def ground_idw(self, distance_coefficient, extent, interporation_data, column, row):
        output = (
            os.path.dirname(interporation_data)
            + "/"
            + os.path.basename(interporation_data).split(".")[0]
            + "_idw.asc"
        )
        alg = {
            "DISTANCE_COEFFICIENT": distance_coefficient,
            "EXTENT": extent,
            "INTERPOLATION_DATA": interporation_data + "::~::0::~::1::~::0",
            "OUTPUT": output,
            "COLUMNS": column,
            "ROWS": row,
        }
        processing.run("qgis:idwinterpolation", alg)
        return output

    # 위성 shp 생성
    def point2raster(self, input_shp, input_sat):
        print("POINT2RASTER")
        output = (
            os.path.dirname(input_sat)
            + "/"
            + os.path.basename(input_sat).split(".")[0]
            + "_RS.shp"
        )
        print(output)
        alg = {
            "COLUMN_PREFIX": "rvalue",
            "INPUT": input_shp,
            "OUTPUT": output,
            "RASTERCOPY": input_sat,
        }
        print(alg)
        processing.run("qgis:rastersampling", alg)
        return output

    # 위성데티어 IDW 보간-CREATE SAT2
    def SAT_idw(self, distance_coefficient, extent, interporation_data, column, row):
        print("SAT_IDW")
        output = (
            os.path.dirname(interporation_data)
            + "/"
            + os.path.basename(interporation_data).split(".")[0]
            + "_idw.asc"
        )
        alg = {
            "DISTANCE_COEFFICIENT": distance_coefficient,
            "EXTENT": extent,
            "INTERPOLATION_DATA": interporation_data + "::~::0::~::2::~::0",
            "OUTPUT": output,
            "COLUMNS": column,
            "ROWS": row,
        }
        processing.run("qgis:idwinterpolation", alg)
        return output

    # DIFF = SAT2-GROUND_IDW
    def calculator_diff(self, SAT2, ground_idw):
        print("calculator_diff")
        output = (
            os.path.dirname(SAT2)
            + "/"
            + os.path.basename(SAT2).split(".")[0]
            + "_"
            + os.path.basename(ground_idw).split(".")[0]
            + "_DIFF.asc"
        )
        alg = 'gdal_calc --calc "A-B" --format GTiff --type Float32 -A "{0}" --A_band 1 -B "{1}" --B_band 1 --outfile "{2}" '.format(
            SAT2, ground_idw, output
        )
        os.system(alg)
        print(output)
        return output

    # SAT - DIFF
    def calc_CMmethod(self, SAT, DIFF):
        print("calcCMmethod")
        output = os.path.dirname(SAT) + os.path.basename(SAT).split(".")[0] + "_cm.asc"
        alg = 'gdal_calc --calc "A-B" --format GTiff --type Float32 -A "{0}" --A_band 1 -B "{1}" --B_band 1 --outfile "{2}" '.format(
            SAT, DIFF, output
        )
        os.system(alg)
        return output
