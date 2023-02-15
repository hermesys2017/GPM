# -*- coding: utf-8 -*-

'''

/***************************************************************************

    Created on 2019. 4. 29.
    
    @author: MH.CHO

***************************************************************************/
'''

import os,sys
from math import sqrt
import numpy

class Util_satellitecorrection():
    def getdist(self,colwidth,rowwidth):
        dist = sqrt(pow(colwidth,2) + pow(rowwidth,2))
        return dist
    
    #연세대 sample 데이터 전용 km 반환
    def getdist_YSU_SampleData_Only(self,colwidth, rowwidth):
        dist_km=sqrt(   pow((colwidth/4.0*91.290),2)  +  pow((rowwidth/4.0*110.941),2)    )
        # /4 이유는 모로코 격자 규격이 0.25도 간격 이라서.. 거리 수치는 소스에서 가져옴  
        # 우리가 http://www.nhc.noaa.gov/gccalc.shtml 에서 확보한 수치와 거의 비슷함  
        return dist_km  
    
    #noata를 제외한 격자 전체 평균
    def total_mean(self,matrix,nodata):
        total_mean =numpy.mean(numpy.ma.masked_values(matrix,nodata))
        return total_mean
    
    #표준편차 함수만 오류를 일으키고 있음.
    #nodata를 제외한 격자 전체 표준편차
    def total_stdev(self,matrix, nodata):
        total_stdev = numpy.std(numpy.ma.masked_values(matrix,nodata))
        return total_stdev
    
    # 파일 이름만 가져오기.
    def GetFileName(self,file):
        return (str(os.path.split(os.path.splitext(file)[0])[1]))
    
    def header_ncols(self,obsData):
        file = open(obsData)
        dataItems = file.read().split()
        
        for i in range(5):
            if (dataItems[i].lower() == 'ncols'):
                ncols = int(dataItems[i+1])
            
        return ncols
    
    def obsData_body(self,obsData):
        file = open(obsData)
        body = numpy.loadtxt(obsData,skiprows=(6))
        
        return body    