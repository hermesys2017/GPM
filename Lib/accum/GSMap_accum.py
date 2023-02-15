# -*- coding: utf-8 -*-
'''
Created on 2019. 10. 30.

GSMap 누적강우 처리 모듈
1시간 데이터임
3시간 부터 적용

@author: USER
'''
import os,sys

import Util

import util_accum

_util = Util.util()
_utilAC = util_accum.accum_util()
#=== 3H ====
def accum_GSMap_3H(folder,list):
    try:
        H3hour_list=[]
        if os.path.exists(folder+"/3H/") == False:
            os.mkdir(folder+"/3H/")
            
        for f_accum in list:
            filename=_util.GetFilename(f_accum)
            outputname = folder+"/3H/"+filename+"_3H.tif"    
            H3hour_list.append(f_accum)
            if len(H3hour_list) > 3:
                del H3hour_list[0:3]
                
            if len(H3hour_list) == 3:
                _utilAC.Accum_hour(H3hour_list,outputname)
    except Exception as exc:
        return str(exc)
    
# ==== 6H =======
def accum_GSMap_6H(folder,list):
    try:
        H6hour_list=[]
        if os.path.exists(folder+"/6H/") == False:
            os.mkdir(folder+"/6H/")
            
        for f_accum in list:
            filename=_util.GetFilename(f_accum)
            outputname = folder+"/6H/"+filename+"_6H.tif"    
            H6hour_list.append(f_accum)
            if len(H6hour_list) > 6:
                del H6hour_list[0:6]
                
            if len(H6hour_list) == 6:
                _utilAC.Accum_hour(H6hour_list,outputname)
    except Exception as exc:
        return str(exc)
    

# ==== 9H ======
def accum_GSMap_9H(folder,list):
    try:
        H9hour_list=[]
        if os.path.exists(folder+"/9H/") == False:
            os.mkdir(folder+"/9H/")
            
        for f_accum in list:
            filename=_util.GetFilename(f_accum)
            outputname = folder+"/9H/"+filename+"_9H.tif"    
            H9hour_list.append(f_accum)
            if len(H9hour_list) > 9:
                del H9hour_list[0:9]
            if len(H9hour_list) == 9:
#                         QgsMessageLog.logMessage(str(H9hour_list),"GPM Accum Run 9H")
                _utilAC.Accum_hour(H9hour_list,outputname)
        
        
    except Exception as exc:
        return str(exc)

# ==== 12H =======
def accum_GSMap_12H(folder,list):
    try:
        H12hour_list=[]
        if os.path.exists(folder+"/12H/") == False:
            os.mkdir(folder+"/12H/")
        
        for f_accum in list:
            filename=_util.GetFilename(f_accum)
            outputname = folder+"/12H/"+filename+"_12H.tif"       
            H12hour_list.append(f_accum)
            if len(H12hour_list) > 12:
                del H12hour_list[0:12]
            if len(H12hour_list) == 12:
                _utilAC.Accum_hour(H12hour_list,outputname)
    except Exception as exc:
        return str(exc)
    
# ==== 24H =======
def accum_GSMap_24H(folder,list):
    try:
        H24hour_list=[]
        if os.path.exists(folder+"/24H/") == False:
            os.mkdir(folder+"/24H/")
        for f_accum in list:
            filename=_util.GetFilename(f_accum)
            outputname = folder+"/24H/"+filename+"_24H.tif"   
            H24hour_list.append(f_accum)
            if len(H24hour_list)>24:
                del H24hour_list[0:24]
            if len(H24hour_list) == 24:
                _utilAC.Accum_hour(H24hour_list,outputname)
    except Exception as exc:
        return str(exc)