# -*- coding: utf-8 -*-
'''
Created on 2018. 11. 14.

@author: MHCHO
'''

import gdal,gdalconst,osr
import osgeo.gdalnumeric as gdn
import numpy
import os

class transpose_Tiff_class():
    def img_to_array(self,input_tiff,output_tiff):
    #    output = os.getenv('USERPROFILE') + '\\Desktop\\' + "output_test.asc"
    #    outputFile = open(output,"w+")
    #     input_file ="D:/Working/Gungiyeon/GPM/GPM_test/T20181113/test_input.tif"
    #    out_data = "D:/Working/Gungiyeon/GPM/GPM_test/T20181113/output.tif"
        
        #고정값
        dim_ordering="channels_last"
        dtype='float32'
        file  = gdal.Open(input_tiff)
        bands = [file.GetRasterBand(i) for i in range(1, file.RasterCount + 1)]
    #    arr = np.array([gdn.BandReadAsArray(band) for band in bands]).astype(dtype)
        arr=numpy.array(file.GetRasterBand(1).ReadAsArray())
    #     print arr.shape[0],arr.shape[1]
            
        driver = gdal.GetDriverByName("GTiff")
    #     out_data = "D:/Working/Gungiyeon/GPM/GPM_test/T20181113/output_4.tif"
    #     output_tiff = _util.GetFilename(input_tiff) #이 부분을 getfilename,  후 이름+_transpose.tif 로 변경
        
        # ======== 이건 고정값
        DataType = gdal.GDT_Float32 
        prj = osr.SpatialReference()
        prj.ImportFromEPSG(4326) # WGS84
        #========
        try:
            if dim_ordering=="channels_last":
                arr = numpy.transpose(arr)  # Reorders dimensions, so that channels are last
                
                out_tif = driver.Create(output_tiff, arr.shape[1], arr.shape[0], 1,DataType)
                out_tif.SetProjection(prj.ExportToWkt())
                out_band = out_tif.GetRasterBand(1)
                out_band.WriteArray(arr)
                out_tif.FlushCache()
                out_tif = None
                
        except Exception as e:
            return str(e)
    #         print arr.shape[0],arr.shape[1]
    #        outputFile.write(str(arr).replace("[","").replace("]","")+"\n")
    #    print arr
    #    outputFile.close()
    #     return arr
    
