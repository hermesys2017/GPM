# -*- coding: utf-8 -*-
"""
/***************************************************************************
 kict_satellite
                                 A QGIS plugin
 KICT Satellite Beta Plugin
                              -------------------
        begin                : 2017-06-02
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Hermesys
        author               : MinHye Jo
        email                : mhcho058@hermesys.co.kr
        
        Remark               : KICT provided algorithm.        
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

import os,sys
import platform
from math import sqrt,e
import numpy
# import header_class
from time import sleep
import time
import datetime

# sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/Lib')
import util_satellitecorrection as util_sc

# g_distance_km=0
ErrOneMsg =""
InformMsg=""

# _util = Util.util()
# _header = header_class.header_body()
_util_sc = util_sc.Util_satellitecorrection()
class satellite_correction():
    # asc 를 불러오고 cols, rows를 받아오는 함수
#     def Get_ASC_header_and_body(self,asc_file):
#         global ErrOneMsg #오류 메시지를 모음
#          
#         satellite_read = open(asc_file)
#         dataItems = satellite_read.read().split()#읽은 위성관측자료의 데이터를 split() 함
#          
#         #위성관측 자료 데이터 값, 여기서 처리
#         _header.body = numpy.loadtxt(asc_file,skiprows= (6))
# #         self.body = numpy.loadtxt(asc_file,skiprows= (6))           
#          
#         try:
#             for i in range(20):
#                 if  (dataItems[i].lower() == 'ncols') :
#                     _header.ncols = int(dataItems[i+1])
# #                     self.ncols= int(dataItems[i+1])
#                 if  (dataItems[i].lower() == 'nrows') :
#                     _header.nrows = int(dataItems[i+1])
#                     self.nrows = int(dataItems[i+1])
#                 if (dataItems[i].lower() == 'xllcorner'):
#                     _header.xllcorner = float(dataItems[i+1])
# #                     self.xllcorner= float(dataItems[i+1])
#                 if (dataItems[i].lower() == 'yllcorner'):
#                     _header.yllcorner = float(dataItems[i+1])
# #                     self.yllcorner= float(dataItems[i+1])
#                 if (dataItems[i].lower() == 'cellsize'):
#                     _header.cellsize = float(dataItems[i+1])
# #                     self.cellsize= float(dataItems[i+1])
#                 if (dataItems[i].lower() == 'nodata_value'):
#                     _header.nodata_value = float(dataItems[i+1])
# #                     self.nodata_value = float(dataItems[i+1])
#                      
#             #파일을 이제 닫아요.
#             satellite_read.close()
#              
#         except Exception as exc:
#             strErrmsg = "Get_ASC_header_and_body :"+str(exc)
#             if strErrmsg not in ErrOneMsg:
#                 ErrOneMsg= ErrOneMsg + strErrmsg+" / "
#             return False
    
        
    # 모든 함수를 처리하는 main 함수
    def run_correction(self,save_path,asc_file_list,groundFile_list,_decimal):
        global InformMsg
        result_msg = ""
        '''
        # 위성관측자료(ASC)와 지상관측자료(CSV)는 1:1 대응하여 보정처리가 되는 것임.
        # 따라서 현재는 ASC : CSV = 1:n 대응임.
        # 그래서 1:n 대응을 1:1 대응으로 코드 변경 필요...
        #How to...?
        '''
#         print ("START")
        start_time_GPM = time.time()
        
        start_time_date= (datetime.datetime.now())
        print ("START TIME :",start_time_date)
        
        
        for count in range(len(asc_file_list)):
#         for asc_file in asc_file_list :
            InformMsg=""
            #어차피 asc 는 한번 들어옴... 1:1 대응(ASC:CSV)
            self.sat_data=str(asc_file_list[count])
            
            self.ncols=_util_sc.header_ncols(self.sat_data)
            self.nrows=_util_sc.header_nrows(self.sat_data)
            self.xllcorner=_util_sc.header_xllcorner(self.sat_data)
            self.yllcorner=_util_sc.header_yllcorner(self.sat_data)
            self.cellsize=_util_sc.header_cellsize(self.sat_data)
            self.nodata_value=_util_sc.header_nodata(self.sat_data)
            self.body=_util_sc.obsData_body(self.sat_data)
            
#             self.Get_ASC_header_and_body(self.sat_data)
            
            
            self.Get_ground_matrix(str(groundFile_list[count]))
            self.Get_Ground_Point(str(groundFile_list[count]))

            save_sre_correction = self.Correction_and_saveResult(save_path,str(groundFile_list[count]), self.sat_data,_decimal)
            
            result_msg = result_msg+str(save_sre_correction)
            print (result_msg)
#             print (datetime.datetime.now())
            print (datetime.datetime.now()-start_time_date)
            print("FIN time :", time.time() - start_time_GPM)
        return str(result_msg)

    
    #2017/12/03 csv file format
    #map좌표를 row, cols 좌표로 변환하는 함수
    def row_cols_calc(self,csv_file):
        global InformMsg
        
#         xmin = _header.xllcorner; ymax = _header.yllcorner + ((_header.nrows) * (_header.cellsize))
#         ysize = _header.cellsize; xsize = _header.cellsize
        
        xmin = self.xllcorner; ymax = self.yllcorner + ((self.nrows) * (self.cellsize))
        ysize = self.cellsize; xsize = self.cellsize
                 
#         read_csv_file=open(csv_file).read().split()
        read_ground_file = open(csv_file)
        
        split_file =read_ground_file.read().split()
        
        csv_matrix = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)]
        #래스터 cell에 멸 개의 data가 들어 있는지 담는 2차원 배열
        count_mat = [[1 for xx in range(self.ncols)] for yy in range(self.nrows)]
               
#         csv_matrix = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)]
#         #래스터 cell에 멸 개의 data가 들어 있는지 담는 2차원 배열
#         count_mat = [[1 for xx in range(self.ncols)] for yy in range(self.nrows)]
        
        count =1 
        for i in range(len(split_file)):
            row_list=[];column_list=[];value_list=[];
            csv_r_value = split_file[i].split(",")
             
            row = int(((ymax -float(csv_r_value[1]) ) / ysize))
            column= int(((float(csv_r_value[0]) - xmin) / xsize)) 
                          
            row_list.append(row); column_list.append(column);value_list.append(float(csv_r_value[2]))  
            
            try:
                #동일한 cell에 데이처 값이 있는 경우 처리
                if csv_matrix[row_list[0]][column_list[0]] != (self.nodata_value):
                    count += 1
                    #동일한 cell에 값이 있는 경우 데이터 합
                    value_list[0] = (csv_matrix[row_list[0]][column_list[0]] + value_list[0])
                    strInfomMsg ="Several data within the same cell. /t :: row,cols :(" + str(row_list[0]) +", " + str(column_list[0]) + ")"
                    if strInfomMsg not in InformMsg:
                        InformMsg += strInfomMsg + " / "
                else:
                    count = 1
                
                csv_matrix[row_list[0]][column_list[0]] = value_list[0]
                count_mat[row_list[0]][column_list[0]]  = count
 
            except Exception as exc:
                #이 부분은 후에 처리 메시지를 띄워야 함
                 
                strInfomMsg = str(exc) + ":: row,cols : (" + str(row_list[0]) +", " + str(column_list[0]) + ")"
                if strInfomMsg not in InformMsg:
                    InformMsg += strInfomMsg + " / "
#                 print exc, (row_list[0], column_list[0])
                 
                del row_list[0]; del column_list[0]
                pass
        
        

        #최종 나온 결과 matrix에서 count가 2이상인 경우 평균을 내야 함으로 나눈다.
        for yrow in range(self.nrows):
            for xcols in range(self.ncols):
                if csv_matrix[yrow][xcols] !=(self.nodata_value):
                    if 2<= count_mat[yrow][xcols]:
                        csv_matrix[yrow][xcols] = csv_matrix[yrow][xcols]/count_mat[yrow][xcols]
         
         
        ground_rows = len(csv_matrix)
        ground_cols =  len(csv_matrix[0])
         
        ground_data = []
        
        for y in range(ground_rows):
            for x in range(ground_cols):
                if csv_matrix[y][x] != (self.nodata_value):
                    ground_data.append((csv_matrix[y][x]))
                     
    #    지상 관측 데이터 에서 NO_DATA 아닌 값의 갯수
    #nodata 값은 asc 마다 다르니.. _header 클래스에서 받은 값으로~~
        self.ground_point = len(ground_data)
        #지상 관측 데이터의 전체 평균
        self.total_avg_obs = numpy.mean(ground_data)
    #     #지상 관측 데이터의 전체 표준편차
        self.total_std_obs = numpy.std(ground_data)
        
        ##csv 파일을 닫아줍시다~
        read_ground_file.close()
    
    
    # # 갯수 관측 점
    def Get_Ground_Point(self,groundFile):
        #파일 확장자에 따라 분기
        if os.path.splitext(groundFile)[1].lower() == ".csv":
            return self.row_cols_calc(groundFile)

        elif os.path.basename(groundFile).split(".")[1].lower() == "asc":
            #지상 데이터 파일을 읽어옴
            ground_file = numpy.loadtxt(groundFile,skiprows=(6))
            
            #지상 데이터 파일의 cols 값
            ground_cols = ground_file.shape[1]
            #지상 데이터 파일의 rows 값
            ground_rows = ground_file.shape[0]
            # 지상 관측 점
            ground_data = []
            for y in range(ground_rows):
                for x in range(ground_cols):
                    if ground_file[y][x] != (self.nodata_value):
                        ground_data.append(ground_file[y][x])
            
            #지상 데이터 중 no_data(-999)가 아닌 값의 갯수
            self.ground_point = len(ground_data)
            #지상 데이터의 전체 평균
            self.total_avg_obs = numpy.mean(ground_data)
            #지상 데이터의 전체 표준편차
            #numpy 외부 라이브러리에서 표준편차는 기본적으로 모표준편차를 다룬다.
            self.total_std_obs = numpy.std(ground_data)
            
#             return ground_point,total_avg_obs,total_std_obs
        elif (os.path.exists(groundFile)) == False:
            return False
    
    
    
    #2017/12/06 ==================
    def csv_matrix(self,groundFile):
        global InformMsg
        
        ground_csv_file = open(groundFile)
        read_csv_file=ground_csv_file.read().split()
        
        xmin = self.xllcorner; ymax = self.yllcorner + ((self.nrows) * (self.cellsize))
        ysize = self.cellsize; xsize = self.cellsize
        
        #여기서 matrix의 cols row가 문제가 됨
        groundFile_matrix = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)]
        #count 갯수 담는 2차원 배열
        count_mat = [[1 for xx in range(self.ncols)] for yy in range(self.nrows)]
        
        count = 1
        for i in range(len(read_csv_file)):
            row_list=[];column_list=[];value_list=[]
            csv_r_value = read_csv_file[i].split(",")
#             csv_r_value= (*map(float,csv_r_value))
            
            row = int(((ymax -(float(csv_r_value[1])) ) / ysize))
            column= int(((float(csv_r_value[0]) - xmin) / xsize))
#             print (row, column)
            
            row_list.append(row); column_list.append(column); value_list.append(float(csv_r_value[2])) 
            
            try:
                
                if groundFile_matrix[row_list[0]][column_list[0]] != self.nodata_value:
                    count += 1
                    
                    #동일한 cell에 값이 있는 경우 데이터 합
                    value_list[0] = groundFile_matrix[row_list[0]][column_list[0]] + value_list[0]
                    strInfomMsg ="Several data within the same cell. /t :: row,cols :(" + str(row_list[0]) +", " + str(column_list[0]) + ")"
                    if strInfomMsg not in InformMsg:
                        InformMsg += strInfomMsg + " / "
                
                else:
                    count = 1
                
                groundFile_matrix[row_list[0]][column_list[0]] = value_list[0]
                count_mat[row_list[0]][column_list[0]]  = count
                
            except Exception as exc:
                print (str(exc))
                strInfomMsg = str(exc)
                if strInfomMsg not in InformMsg:
                    InformMsg += strInfomMsg + " / "
                
                
                #이 부분은 후에 처리 메시지를 띄워야 함
#                 print exc, (row_list[0], column_list[0])
                
                del row_list[0]; del column_list[0]
                pass
                
        #최종 나온 결과 matrix에서 count가 2이상인 경우 평균을 내야 함으로 나눈다.
        for yrow in range(self.nrows):
            for xcols in range(self.ncols):
                if groundFile_matrix[yrow][xcols] !=(self.nodata_value):
                    if 2<= count_mat[yrow][xcols]:
                        groundFile_matrix[yrow][xcols] = groundFile_matrix[yrow][xcols]/count_mat[yrow][xcols]
#         debug.write(groundFile_matrix)
#         debug.close()
        ground_csv_file.close()
        return groundFile_matrix        
        
    #거리 얻는 방법 분기(연세대 샘플 파일만 별개로 하기 위함)
#     def Getdist_if(self, asc_file, ncols_x, nrows_y, x, y):
    def Getdist_if(self, ncols_x, nrows_y, x, y):
        global ErrOneMsg
        try:
            if os.path.basename(self.sat_data).lower() == "yeonsei_testcase.asc": 
#                 dist_km_between_cells=self.getdist_YSU_SampleData_Only(x-ncols_x,y-nrows_y)#피타고라스, 위치로부터 거리로 계산
                dist_km_between_cells=_util_sc.getdist_YSU_SampleData_Only(x-ncols_x,y-nrows_y)#피타고라스, 위치로부터 거리로 계산
                
            else:
#                 dist_km_between_cells=self.getdist(x-ncols_x,y-nrows_y)
                dist_km_between_cells=_util_sc.getdist(x-ncols_x,y-nrows_y)
            return dist_km_between_cells
        
        except Exception as e:
            strErrOnemsg ="Getdist_if :"+str(e)
            if strErrOnemsg not in ErrOneMsg:
                ErrOneMsg=  ErrOneMsg+ strErrOnemsg + " / "
            
        
    #지상강우파일 포맷에 따라 격자 생성
    def Get_ground_matrix(self, groundFile):
        global ErrOneMsg
        try:
            #csv 파일 포맷인 경우
            if os.path.splitext(groundFile)[1].lower() == ".csv":
                self.ground_file = self.csv_matrix(groundFile)
            if os.path.splitext(groundFile)[1].lower() == ".asc":
                self.ground_file = numpy.loadtxt(groundFile,skiprows=(6))
                
#             return ground_file
        except Exception as e:
            strErrOnemsg = "Get_ground_matrix : " + str(e)
            if strErrOnemsg not in ErrOneMsg:
                ErrOneMsg=  ErrOneMsg+ strErrOnemsg + " / "
#                 ErrOneMsg+= strErrOnemsg+" / "
                

    # 지상자료의 평균 : m_obs    .2017.8.3 ice.
#     def AVG_OBS_ZONE(self,groundFile,asc_file):
    def AVG_OBS_ZONE(self,asc_file):
        global ErrOneMsg #오류 메시지를 모음
        try:
            #최종적으로 지상 데이터 파일의 평균값이 들어가는 격자
            self.ground_avg_matrix = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)]
            
            #개수를 세어 둔 격자
            self.ground_count_matrix = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)] #2017.8.22 원 : 신설
            
    #         #계산
            
            for y in range(self.nrows):
                for x in range(self.ncols):
                    if self.g_final_dist[y][x] >0:
                        continue
                    
                    
                    intSum = 0.0 ; ground_data_count = 0
#                     t_mask = [[0 for x2 in range(_header.ncols)] for y2 in range(_header.nrows)]
#                     t_mask = [[0 for x2 in range(self.ncols)] for y2 in range(self.nrows)]
                    #채택 여부 구분.. 여기 x,y 사용시 외부 index 영향줌
                    #기존의 scope 변수를 distance로 변경함
                    for nrows_y in range(self.nrows):
                        for ncols_x in range(self.ncols):
                            # python array 초과index 에선는 exception.  0 아래로 가는 경우 오류가 아니라.. 돌아서 값을 반환.. 
                            #따라서 0이상부터 시작하게 조정.
                            if nrows_y >= 0 and ncols_x >= 0:
                                try:
                                    #dist_km_between_cells=((x-ncols_x)**2 + (y-nrows_y)**2)**0.5
                                    #거리를 계산한다. 4번 사용되는 아이라 분리했음
#                                     dist_km_between_cells = self.Getdist_if(asc_file, ncols_x, nrows_y, x, y)
                                    
#                                     if self.g_distance_km >= dist_km_between_cells :
                                    if self.g_distance_km >= self.Getdist_if(ncols_x, nrows_y, x, y) :
                                        
                                        #t_mask는 어디가 선택된것인지 확인하는 용도임    
#                                         t_mask[nrows_y][ncols_x]=1
#                                         print (t_mask)
                                        
                                        if self.ground_file[nrows_y][ncols_x]!=(self.nodata_value):
                                            intSum = intSum + self.ground_file[nrows_y][ncols_x]
                                            ground_data_count = ground_data_count + 1
                                            
                                except IndexError:
                                    pass
                                except Exception as exc:
                                    strErrOnemsg = "AVG_OBS_ZONE :"+str(exc)
                                    if strErrOnemsg not in ErrOneMsg:
                                        ErrOneMsg+= strErrOnemsg+" / "
                    
                    self.ground_avg_matrix[y][x]=intSum
                    self.ground_count_matrix[y][x] = ground_data_count

                    if ground_data_count >0:
                        self.ground_avg_matrix[y][x] = self.ground_avg_matrix[y][x]/ground_data_count
                    
                    elif ground_data_count<1:
                        self.ground_avg_matrix[y][x] = self.total_avg_obs
            
        except Exception as exc:
            str_errmsg= (exc)   
            if str_errmsg not in ErrOneMsg:
                ErrOneMsg=ErrOneMsg+str_errmsg+" / "
    
    
#     # 2017/8 원 : 기존엔 col,row 격자 cell 거리 방식이었고. 이제 km 단위로 변경함
#     #연대 sample 데이터 전용으로 km를 반환
#     def getdist_YSU_SampleData_Only(self,colwidth,rowwidth):
#     #     dist_km=(   ((colwidth/4.0*91.290)**2)  +  ((rowwidth/4.0*110.941)**2)    )**0.5
#         dist_km=sqrt(   pow((colwidth/4.0*91.290),2)  +  pow((rowwidth/4.0*110.941),2)    )
#         # /4 이유는 모로코 격자 규격이 0.25도 간격 이라서.. 거리 수치는 소스에서 가져옴  
#         # 우리가 http://www.nhc.noaa.gov/gccalc.shtml 에서 확보한 수치와 거의 비슷함  
#         return dist_km  
    
    # #지상자료의 표준 편차(지상자료의 평균 사용) : t_OBS
#     def STDEV_OBS_ZONE(self,groundFile,asc_file):
    def STDEV_OBS_ZONE(self,asc_file):
#         global g_final_dist
        global ErrOneMsg #오류 메시지를 모음

        #여기엔 표준편차 격자를 담을 거야
        self.stdev_obs_matrix = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)]
         
        for y in range(self.nrows):
            for x in range(self.ncols):        
                if self.g_final_dist[y][x] >0:
                    continue 
                ground_data_count = 0 ; tau_obs_arr = [] ;
                for nrows_y in range(self.nrows):
                    for ncols_x in range(self.ncols):
                        if nrows_y >= 0 and ncols_x >=0:
                            try:
                                if self.g_distance_km >= self.Getdist_if(ncols_x, nrows_y, x, y) :
                                    
                                    if (self.ground_file)[nrows_y][ncols_x]!=(self.nodata_value):
                                        AVG2DATA= (self.ground_avg_matrix)[y][x]-(self.ground_file)[nrows_y][ncols_x]
                                        tau_obs_arr.append(AVG2DATA)
                                        
                            except IndexError:
                                pass
                            except Exception as exc:
                                strErrOnemsg = "STDEV_OBS_ZONE :"+str(exc)
                                if strErrOnemsg not in ErrOneMsg:
                                    ErrOneMsg=ErrOneMsg + "STDEV_OBS_ZONE : " +strErrOnemsg+" / "      
                                return False          
                 
                if len(tau_obs_arr) > 0:
                    self.stdev_obs_matrix[y][x] = numpy.std(tau_obs_arr)
                elif ground_data_count <1:
                    self.stdev_obs_matrix[y][x] = self.total_std_obs
                    
   
    #보정 전 위성 평균
#     def AVG_SRE_ZONE(self,groundFile, asc_file):
    def AVG_SRE_ZONE(self,groundFile):
        
        global ErrOneMsg #오류 메시지를 모음
        
        #여기에 평균 sre 값을 넣을 거야
        self.avg_sre_matrix = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)] 
    
        #위성자료의 평균을 구함
        '''
                    이전까지는 위성강우와 지상강우가 일치하는 위치의 값만을 사용했으나, 연세대의 결과 값을 참고하여
                    위성강우의 격자를 그대로 사용
        '''
            
        for y in range(self.nrows):
            for x in range(self.ncols):
                if self.g_final_dist[y][x]>0:
                    continue ##고속화, 조건에 맞는 것만 작업함.. 이미 작업한 곳을 또 작업하지 않음
                #계산
                empty_sum = 0.0 ; sre_sum_arr=[]
                for nrows_y in range(self.nrows):
                    for ncols_x in range(self.ncols):
                        if nrows_y >= 0 and ncols_x >=0:
                            try:
                                if self.g_distance_km >= self.Getdist_if(ncols_x, nrows_y, x, y) :
                                    
                                    empty_sum= empty_sum + (self.body[nrows_y][ncols_x])
                                    sre_sum_arr.append(self.body[nrows_y][ncols_x])
                                    
                                    
                            except IndexError:
                                pass
                            except Exception as exp:
                                strErrOnemsg= "AVG_SRE_ZONE :"+str(exp)
                                if strErrOnemsg not in ErrOneMsg:
                                    ErrOneMsg+=strErrOnemsg+" / "
                                return False
#                 #지상자료와 시공간 일치된 위성자료의 평균(m_sre)
                # 2017.8.21 원,조 : 판단 기준을 지상 갯수, 위성 갯수중에 위성 갯수로 함
                if len(sre_sum_arr) > 1:
                    self.avg_sre_matrix[y][x] = numpy.mean(sre_sum_arr)
                else:
                    #위성 데이터 자료는 값이 존재하기 때문에, 이 곳으로 넘어올 경우 문제가 있는 것이라 간주함.
                    break

    
    #지상자료와 시공간 일치된 위성자료의 표준편차(t_SRE)
#     def STDEV_SRE_ZONE(self,groundFile,asc_file):
    def STDEV_SRE_ZONE(self,groundFile):
        
#         global g_final_dist
        global ErrOneMsg #오류 메시지를 모음
        
        #여기에 sre 표준편차 값을 담을 거야
        self.stdev_sre_matrix = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)]
        
        for y in range(self.nrows):
            for x in range(self.ncols):
                if self.g_final_dist[y][x]>0: 
                    continue
                satellite_data_count = 0;tau_sre_arr =[]
                for nrows_y in range(self.nrows):
                    for ncols_x in range(self.ncols):
                        if nrows_y >= 0 and ncols_x >=0:
                            try:

                                if self.g_distance_km >= self.Getdist_if(ncols_x, nrows_y, x, y) :
                                    AVG2DATA= (self.avg_sre_matrix)[y][x] - (self.body[nrows_y][ncols_x])
                                    tau_sre_arr.append(AVG2DATA)
                                    
                                    #위성 위치 개수
                            except IndexError:
                                pass       
                            except Exception as exp:
                                strErrOnemsg = "STDEV_SRE_ZONE "+str(exp)
                                if strErrOnemsg not in ErrOneMsg:
                                    ErrOneMsg+=strErrOnemsg+" / "     
                                return False
                
                    #2017.8.21 원, 조 : 판단 기준은 지상 개수이고, 계산은 위성 개수임 
                if len(tau_sre_arr)>1:
                    self.stdev_sre_matrix[y][x] = numpy.std(tau_sre_arr)
                else: 
#                     위성의 데이터 수는 NODATA가 없음. 따라서 여기로 넘어오면 잘 못 된 것. 플러그인에선 이것을 메세지로 출력? or 그냥 패쓰??
                    break
  
    #CV를 구하는 함수
    def cv_stdavg(self,groundFile,asc_file):
        global ErrOneMsg #오류 메시지를 모음
        global InformMsg
        
        self.g_distance_km=0
        
        total_mean_sre = _util_sc.total_mean((self.body),(self.nodata_value))
        total_stdeb_sre= _util_sc.total_stdev((self.body),(self.nodata_value))
#         total_mean_sre =numpy.mean(numpy.ma.masked_values(_header.body,_header.nodata_value))
#         total_stdeb_sre = numpy.std(numpy.ma.masked_values(_header.body,_header.nodata_value))
        
        try:
            SreC = [[(self.nodata_value) for x in range(self.ncols)] for y in range(self.nrows)]
             
            thrs = 1.0/e #e는 내장 모듈인 math의 e 를 사용함
            #최종이 되는 거리를 저장함
            self.g_final_dist=[[0 for x in range(self.ncols)] for y in range(self.nrows)]
                
        #     for i in range(ncolsrows[1]):
            for distance_km in range(0,300):
#                 g_distance_km = distance_km
                self.g_distance_km = distance_km
#                 print ("g_distance_km : ",self.g_distance_km)
#                 print (datetime.datetime.now())
                
                obsavgvalue= self.AVG_OBS_ZONE(asc_file) #지상관측자료 평균값
                
                obsstdvalue = self.STDEV_OBS_ZONE(asc_file) #지상관측자료 표준편차값
                
                sreavgvalue= self.AVG_SRE_ZONE(groundFile) #위성관측자료 평균값
                
                srestdvalue = self.STDEV_SRE_ZONE(groundFile) #위성관측자료 표준편차값
#                 create_file.write("/ntime  srestdvalue: " +"%s"%(time.time()-start_time))
                     
                bALLok = True
                for y in range(self.nrows):
                    for x in range(self.ncols):
                        if self.g_final_dist[y][x] ==0 :
                            bALLok = False
                            if self.avg_sre_matrix[y][x] > 0 and self.stdev_sre_matrix[y][x] /self.avg_sre_matrix[y][x] >= thrs:
                                self.g_final_dist[y][x] = distance_km
                                 
                                #지상의 관측소 개수에 따라 계산 법이 달라짐
                                if self.ground_count_matrix[y][x] ==0: #관측소 0개
                                    microF=self.total_avg_obs/total_mean_sre #전체 지상평균/전체 위성평균
                                    tauF=self.total_std_obs/total_stdeb_sre #전체 지상표준편차/ 전체 위성 표준편차
                                    SreC[y][x]=(((self.body[y][x])-total_mean_sre)*tauF)+(total_mean_sre*microF)
                                elif self.ground_count_matrix[y][x] ==1: 
                                    SreC[y][x]=(self.body[y][x])
                                else:#관측소가 0개, 1개도 아닌 그 외일 때
                                    microF=self.ground_avg_matrix[y][x]/self.avg_sre_matrix[y][x]
                                    tauF=self.stdev_obs_matrix[y][x]/self.stdev_sre_matrix[y][x]
                                    SreC[y][x]=(((self.body[y][x])-self.avg_sre_matrix[y][x])*tauF)+(self.avg_sre_matrix[y][x]*microF)
                                             
#                 create_file.write("/nSreC : /n" +str(SreC)) 
                if bALLok == True:
                    break
                
              
            
            return SreC
        
        except Exception as exp:
            strErrOnemsg = "cv_stdavg :"+str(exp)
            if strErrOnemsg not in ErrOneMsg:
                ErrOneMsg+=strErrOnemsg+ " / "
            return False

    
    
    def Correction_and_saveResult(self,save_path,groundFile,asc_file,_decimal):
        global ErrOneMsg
        global InformMsg

        asc_header = "ncols {0}\nnrows {1}\nxllcorner {2}\nyllcorner {3}\ncellsize {4}\nnodata_value {5}\n".format(
            self.ncols,self.nrows,self.xllcorner,self.yllcorner,self.cellsize,self.nodata_value)
        
        
        sre_correction = self.cv_stdavg(groundFile, asc_file)
        print ("sre_correction FIN")
        
#         sleep(0.1)
        
        errmsg = "" #오류 메세지 받아서 처리하는 녀석
        performMsg = "" #특수 조건 메세지
        body=""
          
        #여기서 분기를 갈라야 함
        #보정처리가 된 것은 분기 1로, 안 된 경우는 2로 보냄
        if sre_correction != False:
            '''
            #5/11:: 참고참고
                    지금은 파일명을 어떻게 해야 할지 몰라서 지상관측자료 파일 명으로 출력 파일 명으로 지정하였음
            '''
            save_path_name= save_path+"/"+_util_sc.GetFileName(asc_file)+("_satellite_correction.asc")
            
            save_file_name=open(save_path_name,'w+')
               
            #Header를 받는 부분, 이전보다 간단하게 받아오게 함
            save_file_name.write(asc_header)
        #   #보정처리 결과 값을 받아오는 부분 -- 셀 단위
            for y in range(len(sre_correction)):
                for x in range(len(sre_correction[y])):
                    output_body = str(round(sre_correction[y][x],_decimal))+"\t"
#                     output_body = str(round(sre_correction[y][x],_decimal))+"  "
                    body+= output_body
                body = body+"\n"
            save_file_name.write(body)
            save_file_name.close()
            #보정처리를 문제 없이 수행한 파일에 대해서는 일부러 넣지 않음
            #보정처리에 문제가 발생한 파일만 errmsg로 내보냄
#             suc_msg="<<<Completed>>>/n/n {0}.".format(os.path.basename(asc_file))
            performMsg = performMsg + "Inform : \n[{0}], {1}\n".format(_util_sc.GetFileName(asc_file),InformMsg)
#             print (performMsg)
            return performMsg
              
              
        elif sre_correction == False:
            errmsg = errmsg + "<<<Error>>> \n\n [{0}], {1}\n\n".format(os.path.basename(asc_file),ErrOneMsg) #+ "/n"+str(obsavgvalue)
            return errmsg


      
# sate = satellite_correction()
#                  
# save_path="D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191115/qgis3/console"
# # # asc_file_list=[u"D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191023/5_ASC/10000/CMORPH_V1.0_ADJ_0.25deg-3HLY_20180901_0_Clip_UTM_resample.asc"]
# # # groundFile_list=[u"D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191023/groundData_test/CMORPH_V1.0_ADJ_0.25deg-3HLY_20180901_0_Clip_UTM_resample.csv"]
# asc_file_list=["D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191106/SAT/yeonsei_testcase.asc"]
# groundFile_list=["D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191115/yeonsei_testcase_ground.csv"]
# # # # # asc_file_list=["D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191023/Sat/hanbando_sample/asc/3B-HHR-L.MS.MRG.3IMERG.20191001-S150000-E152959.0900.V06B.30min_Clip_Amount_1H.asc"]
# # # # # groundFile_list=["D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191023/Sat/hanbando_sample/2019100201.csv"]
#          
# _decimal=2
#                 
# sate.run_correction(save_path, asc_file_list, groundFile_list, _decimal)

        
