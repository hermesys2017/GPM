# -*- coding: utf-8 -*-

'''
Created on 2019. 3. 18.

wget 실행 시 프로세스 리스트에 wget.exe 가 실행중인지 아닌지 확인


@author: MH.CHO
'''

import os,sys
from win32com.client import GetObject

def getProcessList():
    PROCESS_LIST=[]
    getObj = GetObject('winmgmts:')
    processes= getObj.InstancesOf('Win32_Process')
    for ps in processes:
        if ("wget.exe" in (ps.Properties_('Name').Value)):
            PROCESS_LIST.append((ps.Properties_('Name').Value))
    
    print len(PROCESS_LIST)
    return len(PROCESS_LIST)
#     if len(PROCESS_LIST)==0:
#         return "100"
#     else:
#         return "-1"
getProcessList()