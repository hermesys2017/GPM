# -*- coding: utf-8 -*-

"""
Created on 2019. 10. 29.

GSMap tiff 포맷으로 변환하는 모듈

@author: mh.cho
"""

import os
import gzip
import shutil
import subprocess


def convert2tiff_GSMap(file, tif_path):
    print("GSMap")

    output = (
        (os.path.dirname(file)) + "/" + (str(os.path.basename(file)).split(".gz")[0])
    )
    # HDR 생성
    HDR_contxt = "{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}\n{9}".format(
        "ncols 3600",
        "nrows 1200",
        "cellsize 0.1",
        "xllcorner 0",
        "yllcorner -60",
        "nodata_value -9999",
        "#nbits 32",
        "#pixeltype float",
        "byteorder lsbfirst",
        "#layout bsq",
    )
    # prj 생성
    prj_contxt = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'

    with gzip.open(file, "rb") as f_in:
        with open(output, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    create_file = output.split(".dat")[0]
    # HDR
    hdr_file = open(create_file + ".HDR", "w")
    hdr_file.write(HDR_contxt)
    hdr_file.close()

    # prj
    prj_file = open(create_file + ".prj", "w")
    prj_file.write(prj_contxt)
    prj_file.close()

    # 이제 TIFF 로 변환(gdal 사용)
    GSMap_tiff = tif_path + "/" + os.path.basename(create_file) + ".tif"
    #     GSMap_tiff = create_file+".tif"
    if os.path.exists(GSMap_tiff):
        pass
    else:
        arg = "gdal_translate -of GTiff {0} {1}".format(output, GSMap_tiff)
        subprocess.call(arg, shell=True)


#
#     os.system(arg)
