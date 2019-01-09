# -*- coding: utf-8 -*-
'''
Created on 2018. 10. 6.

wget bat script class
change log =  2019-01-02 : ftp 경로 수정

@author: MH.CHO
'''

import os
from datetime import datetime,timedelta
import getpass
# import traceback  
# 
# def trace_file():
#     output = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_data_download.txt"
#     while True:
#         try:
#             #check email code here
#             print "Nothing going on here"
#             lets_make_an_error = "error" + 1
#         except:
#             print "Something went wrong, lets write that to a file"
#             errstr = traceback.format_exc()
#             f = open(output,'a')
#             f.write(errstr)
#             f.close()
#             break

def create_bat_script(start,end,folder):
    output = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_data_download.bat"
    
    #제발 사용자 이름에 공백이나 한글을 좀 제거해주셨으면 하는 바램이 있어요...인식 못하는 외국언어가 많아요..
    username = getpass.getuser()
    wget_path = os.path.dirname(os.path.abspath(__file__))+"/Lib/wget.exe"
    wget_path = wget_path.replace(username,"\""+username+"\"")
    
    ftp_user = "jh-kim@kict.re.kr"
    ftp_pass = "jh-kim@kict.re.kr"
#     ftp_path ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/early/"
    ftp_path ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/late/" #2018-12-26 메일에서 late 사용으로 변경됨.

#     url ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/early/"
    url ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/late/" #2018-12-26 메일에서 late 사용으로 변경됨.
    
    daylist = []
    days= datetime.strptime(end, "%Y-%m-%d").date() - datetime.strptime(start, "%Y-%m-%d").date()
    for i in range(days.days):
        timeday= datetime.strptime(start, "%Y-%m-%d").date()+timedelta(+i)
        daylist.append(timeday)
    
    #마지막 날짜는 따로 추가
    timeday=datetime.strptime(end, "%Y-%m-%d").date()
    daylist.append(timeday)
    S_file=[];E_file=[]
     # ===== S부분 =========
    for ss in range(00,24):
        ss= ("%02d"% ss)
        S_name = str(ss)+"0000"
        S2_name = str(ss)+"3000"
        E_name = str(ss)+"2959"# 2959, 5959 반복
        E2_name = str(ss)+ "5959"
        S_file.append(S_name)
        S_file.append(S2_name)
        E_file.append(E_name)
        E_file.append(E2_name)
    
    #폴더 생성
    createTime= datetime.now()
    createTime_folder= "v%s%s%s_%s%s%s"%(createTime.year,createTime.month,createTime.day,createTime.hour,createTime.minute ,createTime.second )
    
    # =======timestamp =========
    timelist=[]
    for tt in range(0000,1411,30):
        tt= ("%04d"% tt)
        timelist.append(tt)
    
    # ============= 2018-10-23 변경 후
    
    
    #이미이전에 있었나요? 지우고 시작합시다.
    if os.path.exists(output):
        os.remove(output)
    file = open(output,'w+')
    list = [] ; i=0 ;arg_str=[] #arg_str=""
    for dd in daylist:
        datefolder= dd.strftime('%Y%m')
        for i in range(len(S_file)):
            # early 사용
#             file1="3B-HHR-E.MS.MRG.3IMERG.{0}-S{1}-E{2}.{3}.V05B.RT-H5".format(dd.strftime('%Y%m%d'),S_file[i],E_file[i],timelist[i]) #2018-12-26 메일에서 late 사용으로 변경됨.
            
            #late 사용
            file1="3B-HHR-L.MS.MRG.3IMERG.{0}-S{1}-E{2}.{3}.V05B.RT-H5".format(dd.strftime('%Y%m%d'),S_file[i],E_file[i],timelist[i])
            arg = wget_path + " -r -nd -P \"""{0}\" ".format(folder+"/"+createTime_folder)+ "--ftp-user=jh-kim@kict.re.kr --ftp-password=jh-kim@kict.re.kr --content-on-error {0}".format(url+datefolder+"/"+file1)
#             print os.system(arg).read()
            arg_str.append(arg)
#             arg_str +=arg +"\n"
            
            file.write(arg+"\n")
#             arg = wget_path + " -r -nd -P /{0} -A ".format("GPM_BAT")+ "\"" +file1+"\"" + " --ftp-user=jh-kim@kict.re.kr --ftp-password=jh-kim@kict.re.kr --content-on-error {0}".format(url)
#             print arg
    file.close()
    
    #2018-11-14 바로 실행 테스트
#     return output
#     return arg_str
# create_bat_script("2014-03-12","2014-03-12","D:/Working/Gungiyeon/GPM/GPM_test/T20181115/0_data")