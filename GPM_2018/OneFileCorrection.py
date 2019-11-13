# -*- coding: utf-8 -*-
"""
/***************************************************************************
 kict_satellite
                                 A QGIS plugin
 KICT Satellite Beta Plugin
                              -------------------
        begin                : 2017-06-02
        copyright            : (C) 2017 by Hermesys
        author               : MinHye Jo
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

import os
from math import sqrt,e
import numpy

g_distance_km=0
magicNumber = 0
scope_n = 0
ErrOneMsg =""

# asc 를 불러오고 cols, rows를 받아오는 함수
def Get_ColsRols_Number_From_OneFile(asc_file):
    global ErrOneMsg #오류 메시지를 모음
    # asc_file 읽어와서 분해
    dataItems = open(asc_file).read().split()
    # ncols, nrows 가 아니면 발생 
    try:
#         for i in range(len(dataItems)):
        for i in range(12):
            if  (dataItems[i].lower() == 'ncols') :
                ncols = int(dataItems[i+1])
            if  (dataItems[i].lower() == 'nrows') :
                nrows = int(dataItems[i+1])
        return ncols, nrows
    except Exception as exc:
        strErrmsg = str(exc)
        if strErrmsg not in ErrOneMsg:
            ErrOneMsg+=strErrmsg+" / "
        return False
# 헤더를 불러오는 함수
def Load_ASC_Header(asc_file):
    global ErrOneMsg #오류 메시지를 모음
    ncolrows = Get_ColsRols_Number_From_OneFile(asc_file)
    
    if ncolrows <> False:
        dataHeaderItems = open(asc_file).readlines()[:6]
        read_lower = [item.lower() for item in dataHeaderItems] #리스트 의 모든 글자를 소문자화 시킴
        try: 
            headerItems=""
            for row in read_lower:
                headerItems = headerItems+row
                if "nodata_value" in row:
                    header = headerItems
                    index_heder= numpy.reshape(header.split(),(6,-1))
                elif "nodata_value" not in row:
                    if "cellsize" in row:
                        header = headerItems
                        index_heder= numpy.reshape(header.split(),(5,-1))   
            return header,index_heder
        except Exception as exc:
            str_errmsg = str(exc)
            if str_errmsg not in ErrOneMsg:
                ErrOneMsg+= str_errmsg + " / "
            return False
    elif ncolrows == False:
        return False
    
    
    '''
    headerItems 리스트에서 [10]번째 자리가 값이 nodata_value인지 아닌지를 구분하여
    헤더를 가져오는 범위를 다르게 지정함
    '''

# asc body를 2차원 배열로 만드는 함수
def ASC_Body_2grid(asc_file):
    global ErrOneMsg #오류 메시지를 모음
    header = Load_ASC_Header(asc_file)[1]
    bodyItems = numpy.loadtxt(asc_file,skiprows=len(header))
    return bodyItems
    
# 모든 함수를 처리하는 main 함수
def main(save_path,asc_file_list,_decimal):
    
    result_msg = ""
    
    for asc_file in asc_file_list :
        myCSVFile = matching_csv2asc(asc_file)
#         sre_corr=cv_stdavg(myCSVFile,asc_file)
        save_sre_correction = Correction_and_saveResult(save_path,myCSVFile, asc_file,_decimal)
        result_msg += save_sre_correction
    return result_msg
        
    
def matching_csv2asc(strASCFileName):
     
    base = os.path.splitext(strASCFileName)[0]
    base2 = base + ("_GROUND.DAT").lower()
    
    return base2
# 
# # 갯수 관측 점
def Get_Ground_Point(groundFile):
#     print os.path.exists(groundFile)
    if (os.path.exists(groundFile)) == True:
        #지상 데이터 파일을 읽어옴
        ground_file = numpy.loadtxt(groundFile)
        #지상 데이터 파일의 cols 값
        ground_cols = ground_file.shape[1]
        #지상 데이터 파일의 rows 값
        ground_rows = ground_file.shape[0]
        # 지상 관측 점
        ground_data = []
        for y in range(ground_rows):
            for x in range(ground_cols):
                if ground_file[y][x] != -999:
                    ground_data.append(ground_file[y][x])
        
        #지상 데이터 중 no_data(-999)가 아닌 값의 갯수
        ground_point = len(ground_data)
        #지상 데이터의 전체 평균
        total_avg_obs = numpy.mean(ground_data)
        #지상 데이터의 전체 표준편차
        #numpy 외부 라이브러리에서 표준편차는 기본적으로 모표준편차를 다룬다.
        total_std_obs = numpy.std(ground_data)
        
        return ground_point,total_avg_obs,total_std_obs
    elif (os.path.exists(groundFile)) == False:
        return False

# 지상자료의 평균 : m_obs    .2017.8.3 ice.
def AVG_OBS_ZONE(groundFile,asc_file):
    global ErrOneMsg #오류 메시지를 모음
    ncolsrows = Get_ColsRols_Number_From_OneFile(asc_file)
    #ncols 가 x nrow가  y
    global g_distance_km #위에서 선언한 전역변수... 글로벌변수를 사용하겠음을 알려줌
    global g_final_dist #이건 왜??

    if (os.path.exists(groundFile)) == True:  
        ground_file = numpy.loadtxt(groundFile)
        
        #최종적으로 지상 데이터 파일의 평균값이 들어가는 격자
        ground_avg_matrix = [[(-999) for x in range(ncolsrows[0])] for y in range(ncolsrows[1])]
        
        #개수를 세어 둔 격자
        ground_count_matrix = [[(-999) for x in range(ncolsrows[0])] for y in range(ncolsrows[1])] #2017.8.22 원 : 신설
        
#         #계산
        for y in range(ncolsrows[1]):
            for x in range(ncolsrows[0]):
                if g_final_dist[y][x] >0:
                    continue
                intSum = 0.0 ; ground_data_count = 0
#                 t_mask = [[0 for x2 in range(ncols)] for y2 in range(nrows)]
                #채택 여부 구분.. 여기 x,y 사용시 외부 index 영향줌
                #기존의 scope 변수를 distance로 변경함
                for nrows_y in range(ncolsrows[1]):
                    for ncols_x in range(ncolsrows[0]):
                        # python array 초과index 에선는 exception.  0 아래로 가는 경우 오류가 아니라.. 돌아서 값을 반환.. 
                        #따라서 0이상부터 시작하게 조정.
                        if nrows_y >= 0 and ncols_x >= 0:
                            try: 
                                #dist_km_between_cells=((x-ncols_x)**2 + (y-nrows_y)**2)**0.5
 
                                if os.path.basename(asc_file).lower() == "yeonsei_testcase.asc": 
                                    dist_km_between_cells=getdist_YSU_SampleData_Only(x-ncols_x,y-nrows_y)#피타고라스, 위치로부터 거리로 계산
                                else:
                                    dist_km_between_cells=getdist(x-ncols_x,y-nrows_y)

                                if g_distance_km >= dist_km_between_cells :
                                    #t_mask는 어디가 선택된것인지 확인하는 용도임    
#                                     t_mask[nrows_y][ncols_x]=1
                                    if ground_file[nrows_y][ncols_x]<>-999:
                                        intSum = intSum + ground_file[nrows_y][ncols_x]
                                        ground_data_count = ground_data_count + 1
                                        
                            except IndexError:
                                pass
                            except Exception as exc:
                                strErrOnemsg = str(exc)
                                if strErrOnemsg not in ErrOneMsg:
                                    ErrOneMsg+= strErrOnemsg+" / "
                
                ground_avg_matrix[y][x]=intSum
                ground_count_matrix[y][x] = ground_data_count
                
                #지상관측 갯수가 0개보다 많은 경우
                if ground_data_count >0:
                    my_AVG_OBS = ground_avg_matrix[y][x] / ground_data_count
                    ground_avg_matrix[y][x] = my_AVG_OBS
                
                elif ground_data_count<1:
                    my_AVG_OBS = Get_Ground_Point(groundFile)[1] #전체 평균
                    ground_avg_matrix[y][x] = my_AVG_OBS
                
        return ground_avg_matrix,ground_count_matrix
       
    elif (os.path.exists(groundFile)) == False:
        str_errmsg = "not found ground data file."
        if str_errmsg not in ErrOneMsg:
            ErrOneMsg+=str_errmsg+" / "
        return False    


# 2017/8 원 : 기존엔 col,row 격자 cell 거리 방식이었고. 이제 km 단위로 변경함
#연대 sample 데이터 전용으로 km를 반환
def getdist_YSU_SampleData_Only(colwidth,rowwidth):
#     dist_km=(   ((colwidth/4.0*91.290)**2)  +  ((rowwidth/4.0*110.941)**2)    )**0.5
    dist_km=sqrt(   pow((colwidth/4.0*91.290),2)  +  pow((rowwidth/4.0*110.941),2)    )
    # /4 이유는 모로코 격자 규격이 0.25도 간격 이라서.. 거리 수치는 소스에서 가져옴  
    # 우리가 http://www.nhc.noaa.gov/gccalc.shtml 에서 확보한 수치와 거의 비슷함  
    return dist_km  

#연대 sample 이외의 데이터를 사용할 때,m를 반환
def getdist(colwidth, rowwidth):
    dist= sqrt(pow(colwidth,2)+pow(rowwidth,2))
#     dist = ((colwidth**2)+(rowwidth**2))**0.5

    return dist
    
# #지상자료의 표준 편차(지상자료의 평균 사용) : t_OBS
def STDEV_OBS_ZONE(groundFile,asc_file):
    global g_final_dist
    global ErrOneMsg #오류 메시지를 모음
    
    #AVG_OBS_ZONE 의 표준편차를 구하면 된다.
    myAVG_OBS=AVG_OBS_ZONE(groundFile,asc_file)
    ncolsrows = Get_ColsRols_Number_From_OneFile(asc_file)
    
    #여기엔 표준편차 격자를 담을 거야
    stdev_obs_matrix = [[-999 for x in range(ncolsrows[0])] for y in range(ncolsrows[1])]
     
#     scope_cellindex = scoping_cellindex(groundFile,asc_file)
    
    if (os.path.exists(groundFile)) == True:  
        ground_file = numpy.loadtxt(groundFile)
        
        
        for y in range(ncolsrows[1]):
            for x in range(ncolsrows[0]):        
                if g_final_dist[y][x] >0:
                    continue 
                ground_data_count = 0 ; tau_obs_arr = [] ;
                for nrows_y in range(ncolsrows[1]):
                    for ncols_x in range(ncolsrows[0]):
                        if nrows_y >= 0 and ncols_x >=0:
                            try:
                                if os.path.basename(asc_file).lower() == "yeonsei_testcase.asc": 
                                    dist_km_between_cells=getdist_YSU_SampleData_Only(x-ncols_x,y-nrows_y)#피타로라스, 위치로부터 거리로 계산
                                else:
                                    dist_km_between_cells=getdist(x-ncols_x,y-nrows_y)
                                 
                                if g_distance_km >= dist_km_between_cells:
                                    if (ground_file)[nrows_y][ncols_x]<>-999:
                                        AVG2DATA= (myAVG_OBS[0])[y][x]-(ground_file)[nrows_y][ncols_x]
                                        tau_obs_arr.append(AVG2DATA)
                            except IndexError:
                                pass
                            except Exception as exc:
                                strErrOnemsg = str(exc)
                                if strErrOnemsg not in ErrOneMsg:
                                    ErrOneMsg+=strErrOnemsg+" / "      
                                return False          
                 
                if len(tau_obs_arr) > 0:
                    tau_obs_value= numpy.std(tau_obs_arr)
                    stdev_obs_matrix[y][x] = tau_obs_value
                elif ground_data_count <1:
                    tau_obs_value = Get_Ground_Point(groundFile)[2]
                    stdev_obs_matrix[y][x] = tau_obs_value
                    
        return stdev_obs_matrix
                        
    elif (os.path.exists(groundFile)) == False:
        return False 
       
# 지상자료와 시공간 일치된 위성자료의 평균 : m_SRE
#보정 전 위성 평균
def AVG_SRE_ZONE(groundFile, asc_file):
    global g_final_dist
    global ErrOneMsg #오류 메시지를 모음
    
    ncolsrows = Get_ColsRols_Number_From_OneFile(asc_file)
    
    #여기에 평균 sre 값을 넣을 거야
    avg_sre_matrix = [[-999 for x in range(ncolsrows[0])] for y in range(ncolsrows[1])] 

    #위성자료의 평균을 구함
    if ncolsrows<>False:
        #sre를 구하기 위한 asc 격자를 불러옴
        sre_matrix = ASC_Body_2grid(asc_file)
        '''
                    이전까지는 위성강우와 지상강우가 일치하는 위치의 값만을 사용했으나, 연세대의 결과 값을 참고하여
                    위성강우의 격자를 그대로 사용
        '''
        
        for y in range(ncolsrows[1]):
            for x in range(ncolsrows[0]):
                if g_final_dist[y][x]>0:
                    continue ##고속화, 조건에 맞는 것만 작업함.. 이미 작업한 곳을 또 작업하지 않음
                #계산
                empty_sum = 0.0 ; sre_sum_arr=[]
                for nrows_y in range(ncolsrows[1]):
                    for ncols_x in range(ncolsrows[0]):
                        if nrows_y >= 0 and ncols_x >=0:
                            try:
#                                 dist_km_between_cells = ((x-ncols_x)**2+(y-nrows_y)**2)**0.5
                                if os.path.basename(asc_file).lower() == "yeonsei_testcase.asc": 
                                    #이 거리 식은 연세대 자료 한정으로 사용하는 것임으로 이렇게 분류함.
                                    dist_km_between_cells=getdist_YSU_SampleData_Only(x-ncols_x,y-nrows_y)#피타로라스, 위치로부터 거리로 계산
                                else:
                                    dist_km_between_cells=getdist(x-ncols_x,y-nrows_y)
                                
                                if g_distance_km >= dist_km_between_cells:
                                    empty_sum= empty_sum + sre_matrix[nrows_y][ncols_x]
                                    sre_sum_arr.append(sre_matrix[nrows_y][ncols_x])
                                
                            except IndexError:
                                pass
                            except Exception as exp:
                                strErrOnemsg= str(exp)
                                if strErrOnemsg not in ErrOneMsg:
                                    ErrOneMsg+=strErrOnemsg+" / "
                                return False
#                 #지상자료와 시공간 일치된 위성자료의 평균(m_sre)
                # 2017.8.21 원,조 : 판단 기준을 지상 갯수, 위성 갯수중에 위성 갯수로 함
                if len(sre_sum_arr) > 1:
                    m_sre = numpy.mean(sre_sum_arr)
#                     m_sre =  empty_sum/satellite_data_count
                    avg_sre_matrix[y][x] = m_sre
                else:
                    #위성 데이터 자료는 값이 존재하기 때문에, 이 곳으로 넘어올 경우 문제가 있는 것이라 간주함.
                    break
                #위성 데이터의 경우, 값이 있기 때문에 else로 온다면 잘못 된 것.
#                     if satellite_data_count>0:
#                         if satellite_data_count <=1:
#                             m_sre = total_avg_sre
#                             avg_sre_matrix[y][x] = m_sre

        return avg_sre_matrix
     
#     elif (os.path.exists(groundFile)) == False:
    elif ncolsrows==False:
        return False


#지상자료와 시공간 일치된 위성자료의 표준편차(t_SRE)
def STDEV_SRE_ZONE(groundFile,asc_file):
    global g_final_dist
    global ErrOneMsg #오류 메시지를 모음
    
    ncolsrows = Get_ColsRols_Number_From_OneFile(asc_file)
    myAVGSRE= AVG_SRE_ZONE(groundFile,asc_file)
#     scope_index=scoping_cellindex(groundFile,asc_file)
    
    #여기에 sre 표준편차 값을 담을 거야
    stdev_sre_matrix = [[-999 for x in range(ncolsrows[0])] for y in range(ncolsrows[1])] 
    
    if myAVGSRE<>False:
        #sre를 구하기 위한 asc 격자를 불러온다
        sre_matrix = ASC_Body_2grid(asc_file)
        
        for y in range(ncolsrows[1]):
            for x in range(ncolsrows[0]):
                if g_final_dist[y][x]>0: 
                    continue
                satellite_data_count = 0;tau_sre_arr =[]
#                for ncols_x in range(x-scope_index,x+scope_index+1):
#                    for nrows_y in range(y-scope_index,y+scope_index+1):
                for nrows_y in range(ncolsrows[1]):
                    for ncols_x in range(ncolsrows[0]):
                        if nrows_y >= 0 and ncols_x >=0:
                            try:
#                                 dist_km_between_cells=((x-ncols_x)**2 + (y-nrows_y)**2)**0.5
                                if os.path.basename(asc_file).lower() == "yeonsei_testcase.asc": 
                                    dist_km_between_cells=getdist_YSU_SampleData_Only(x-ncols_x,y-nrows_y)#피타고라스, 위치로부터 거리로 계산
                                else:
                                    dist_km_between_cells=getdist(x-ncols_x,y-nrows_y)
                                if g_distance_km >= dist_km_between_cells:
                                    AVG2DATA= (myAVGSRE)[y][x] - sre_matrix[nrows_y][ncols_x]
                                    tau_sre_arr.append(AVG2DATA)
                                    #위성 위치 개수
                            except IndexError:
                                pass       
                            except Exception as exp:
                                strErrOnemsg = str(exp)
                                if strErrOnemsg not in ErrOneMsg:
                                    ErrOneMsg+=strErrOnemsg+" / "     
                                return False
                
                    #2017.8.21 원, 조 : 판단 기준은 지상 개수이고, 계산은 위성 개수임 
                if len(tau_sre_arr)>1:
                    tau_sre = numpy.std(tau_sre_arr)
                    stdev_sre_matrix[y][x] = tau_sre
                else: 
#                     위성의 데이터 수는 NODATA가 없음. 따라서 여기로 넘어오면 잘 못 된 것. 플러그인에선 이것을 메세지로 출력? or 그냥 패쓰??
                    break
#                 elif satellite_data_count <=1:
#                     t_sre = (total_std_sre)
#                     stdev_sre_matrix[y][x] = t_sre
                
                
        return stdev_sre_matrix
     
#     elif (os.path.exists(groundFile)) == False:
    elif myAVGSRE==False:
        return False            

#CV를 구하는 함수
def cv_stdavg(groundFile,asc_file):
    global g_distance_km
    global g_final_dist
    global ErrOneMsg #오류 메시지를 모음

    ncolsrows = Get_ColsRols_Number_From_OneFile(asc_file)
    total_mean_sre =numpy.mean(ASC_Body_2grid(asc_file))
    total_stdeb_sre = numpy.std(ASC_Body_2grid(asc_file))
    if ncolsrows <> False:
        try:
            SreC = [["###" for x in range(ncolsrows[0])] for y in range(ncolsrows[1])]
            
            thrs = 1.0/e #e는 내장 모듈인 math의 e 를 사용함
            
            #최종이 되는 거리를 저장함
            g_final_dist=[[0 for x in range(ncolsrows[0])] for y in range(ncolsrows[1])]
            
        #     for i in range(ncolsrows[1]):
            for distance_km in range(0,300):
                g_distance_km = distance_km
        #         print "distance_km : ", g_distance_km #위치를 알기 위한 용도였음
                obsavgvalue= AVG_OBS_ZONE(groundFile, asc_file)
                obsstdvalue = STDEV_OBS_ZONE(groundFile, asc_file)
                sreavgvalue= AVG_SRE_ZONE(groundFile, asc_file)
                srestdvalue = STDEV_SRE_ZONE(groundFile, asc_file)
              
                bALLok = True
                for y in range(ncolsrows[1]):
                    for x in range(ncolsrows[0]):
                        if g_final_dist[y][x] ==0 :
                            bALLok = False
                            if sreavgvalue[y][x] > 0 and srestdvalue[y][x] /sreavgvalue[y][x] >= thrs:
                                g_final_dist[y][x] = distance_km
        
                                #지상의 관측소 개수에 따라 계산 법이 달라짐
                                if obsavgvalue[1][y][x] ==0: #관측소 0개
                                    microF=Get_Ground_Point(groundFile)[1]/total_mean_sre #전체 지상평균/전체 위성평균
                                    tauF=Get_Ground_Point(groundFile)[2]/total_stdeb_sre #전체 지상표준편차/ 전체 위성 표준편차
                                    SreC[y][x]=((ASC_Body_2grid(asc_file)[y][x]-total_mean_sre)*tauF)+(total_mean_sre*microF)
                                elif obsavgvalue[1][y][x] ==1: #관측소 1개
                                    SreC[y][x]=ASC_Body_2grid(asc_file)[y][x]
                                else:#관측소가 0개, 1개도 아닌 그 외일 때
                                    microF=obsavgvalue[0][y][x]/sreavgvalue[y][x]
                                    tauF=obsstdvalue[y][x]/srestdvalue[y][x]
                                    SreC[y][x]=((ASC_Body_2grid(asc_file)[y][x]-sreavgvalue[y][x])*tauF)+(sreavgvalue[y][x]*microF)            
        
        #보정처리가 기존 방식일떄...                        
        #                         SreC[y][x]=round(SreC[y][x],_decimal)
        
                if bALLok == True:
                    break
        
            return SreC
        except Exception as exp:
            strErrOnemsg = str(exp)
            if strErrOnemsg not in ErrOneMsg:
                ErrOneMsg+=strErrOnemsg+ " / "
            return False
        
    elif ncolsrows == False:
        return False


def Correction_and_saveResult(save_path,groundFile,asc_file,_decimal):
    global ErrOneMsg
    asc_header = Load_ASC_Header(asc_file)[0]
    sre_correction = cv_stdavg(groundFile, asc_file)
    
    save_path_name= save_path+"/"+(os.path.basename(asc_file).lower())
    save_file_name=open(save_path_name,'w')
    
    errmsg = "" #오류 메세지 받아서 처리하는 녀석
    body=""
    
    #여기서 분기를 갈라야 함
    #보정처리가 된 것은 분기 1로, 안 된 경우는 2로 보냄
    if sre_correction <> False:
        #Header를 받는 부분, 이전보다 간단하게 받아오게 함
        save_file_name.write(asc_header)
#         for i in range(0,len(asc_header),2):
#             output_header= str(asc_header[i:i+2]).replace("[", "").replace("]", "").replace("'","").replace(",", " ")+"\n"
#             save_file_name.write(output_header)
        
    #   #보정처리 결과 값을 받아오는 부분 -- 셀 단위
        for y in range(len(sre_correction)):
            for x in range(len(sre_correction[y])):
                output_body = str(round(sre_correction[y][x],_decimal))+"  "
                body+= output_body
            body = body+"\n"
        save_file_name.write(body)
        save_file_name.close()

        #보정처리를 문제 없이 수행한 파일에 대해서는 일부러 넣지 않음
        #보정처리에 문제가 발생한 파일만 errmsg로 내보냄
#         suc_msg="<<<Completed>>>\n\n {0}.".format(os.path.basename(asc_file))
        
        return ""
    elif sre_correction == False:
        errmsg = errmsg + "<<<Error>>> \n\n [{0}], {1}\n".format(os.path.basename(asc_file),ErrOneMsg)
        return errmsg
