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
import subprocess as sub

username = getpass.getuser()
    
wget_path = os.path.dirname(os.path.abspath(__file__))+"/Lib/wget/wget.exe"
wget_path = wget_path.replace(username,"\""+(username)+"\"")


# class wget_download:
#     def __init__(self,userOs,Id,Pw,start,end,folder):
#         self.userOs =userOs
#         self.Id =Id
#         self.Pw = Pw
#         self.start =start
#         self.end =end
#         self.folder = folder
#         
#         #bat 생성
#         self.output = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_data_download.bat"
#         #pc username load
#         self.username = getpass.getuser()
#         
#         #실행
# #         self.check_user_osVersion()
#         self.create_bat_script_64()
#         
#         
# 
#     '''
#     버전 체크하는 곳을 임의로 생성..(사용자 본인이 확인하도록함)
#     체크 박스 64bit이면 기존 사용, 체크박스 32bit 면 새로 생성된 것을 사용하도록 함(지금 내가 체크하는 법을 모르겠다)
#     '''
#     def check_user_osVersion(self):
#         if (self.userOs == "64bit"):
#             download = self.create_bat_script_64()
#             for item in download:
#                 print item
#                 
#         elif (self.userOs =="32bit"):
#             self.create_bat_script_32()
#         
#     def create_bat_script_32(self):
#         #제발 사용자 이름에 공백이나 한글을 좀 제거해주셨으면 하는 바램이 있어요...인식 못하는 외국언어가 많아요..
#         wget_path = os.path.dirname(os.path.abspath(__file__))+"/Lib/wget/wget32/wget.exe"
#         wget_path = wget_path.replace(self.username,"\""+(self.username)+"\"")
#         
#     #     ftp_user = "jh-kim@kict.re.kr"
#     #     ftp_pass = "jh-kim@kict.re.kr"
#         ftp_user = str(self.Id )
#         ftp_pass = str(self.Pw)
#     #     ftp_path ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/early/"
#         ftp_path ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/late/" #2018-12-26 메일에서 late 사용으로 변경됨.
#     
#     #     url ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/early/"
#         url ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/late/" #2018-12-26 메일에서 late 사용으로 변경됨.
#         
#         daylist = []
#         days= datetime.strptime(self.end, "%Y-%m-%d").date() - datetime.strptime(self.start, "%Y-%m-%d").date()
#         for i in range(days.days):
#             timeday= datetime.strptime(self.start, "%Y-%m-%d").date()+timedelta(+i)
#             daylist.append(timeday)
#         
#         #마지막 날짜는 따로 추가
#         timeday=datetime.strptime(self.end, "%Y-%m-%d").date()
#         daylist.append(timeday)
#         S_file=[];E_file=[]
#          # ===== S부분 =========
#         for ss in range(00,24):
#             ss= ("%02d"% ss)
#             S_name = str(ss)+"0000"
#             S2_name = str(ss)+"3000"
#             E_name = str(ss)+"2959"# 2959, 5959 반복
#             E2_name = str(ss)+ "5959"
#             S_file.append(S_name)
#             S_file.append(S2_name)
#             E_file.append(E_name)
#             E_file.append(E2_name)
#         
#         #폴더 생성
#         createTime= datetime.now()
#         createTime_folder= "v%s%s%s_%s%s%s"%(createTime.year,createTime.month,createTime.day,createTime.hour,createTime.minute ,createTime.second )
#         
#         # =======timestamp =========
#         timelist=[]
#         for tt in range(0000,1411,30):
#             tt= ("%04d"% tt)
#             timelist.append(tt)
#         
#         # ============= 2018-10-23 변경 후
#         
#         
#         #이미이전에 있었나요? 지우고 시작합시다.
#         if os.path.exists( self.output):
#             os.remove( self.output)
# #         file = open( self.output,'w+')
#         list = [] ; i=0 
#         for dd in daylist:
#             datefolder= dd.strftime('%Y%m')
#             for i in range(len(S_file)):
#                 # early 사용
#     #             file1="3B-HHR-E.MS.MRG.3IMERG.{0}-S{1}-E{2}.{3}.V05B.RT-H5".format(dd.strftime('%Y%m%d'),S_file[i],E_file[i],timelist[i]) #2018-12-26 메일에서 late 사용으로 변경됨.
#                 
#                 #late 사용
#                 file1="3B-HHR-L.MS.MRG.3IMERG.{0}-S{1}-E{2}.{3}.V05B.RT-H5".format(dd.strftime('%Y%m%d'),S_file[i],E_file[i],timelist[i])
#                 arg = wget_path + " -bqc -r -nd -P \"""{0}\" ".format(self.folder+"/"+createTime_folder)+ "--ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(url+datefolder+"/"+file1)) #이건 한번에 받아오는 거라서..파일을 셀 수가 없어
#     #             arg = wget_path + "  -r -nd -P \"""{0}\" ".format(folder+"/"+createTime_folder)+ "--ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(url+datefolder+"/"+file1))
#                 list.append(arg)
# #                 file.write(arg+"\n")
#     #             arg = wget_path + " -r -nd -P /{0} -A ".format("GPM_BAT")+ "\"" +file1+"\"" + " --ftp-user=jh-kim@kict.re.kr --ftp-password=jh-kim@kict.re.kr --content-on-error {0}".format(url)
#     #             print arg
# #         file.close()
#         return list
#     


#NASA GPM
def create_bat_script_64(Id,Pw,start,end,folder):
    output = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_data_download.bat"
    
    
#     ftp_user = "jh-kim@kict.re.kr"
#     ftp_pass = "jh-kim@kict.re.kr"
#         ftp_user = str(self.Id )
#         ftp_pass = str(self.Pw)
    ftp_user = str(Id )
    ftp_pass = str(Pw)
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
    if os.path.exists( output):
        os.remove( output)
#         file = open( self.output,'w+')
    list = [] ; 
    i=0 
    for dd in daylist:
        datefolder= dd.strftime('%Y%m')
        for i in range(len(S_file)):
            # early 사용
#             file1="3B-HHR-E.MS.MRG.3IMERG.{0}-S{1}-E{2}.{3}.V05B.RT-H5".format(dd.strftime('%Y%m%d'),S_file[i],E_file[i],timelist[i]) #2018-12-26 메일에서 late 사용으로 변경됨.
            
            #late 사용
            file1="3B-HHR-L.MS.MRG.3IMERG.{0}-S{1}-E{2}.{3}.V05B.RT-H5".format(dd.strftime('%Y%m%d'),S_file[i],E_file[i],timelist[i])
#                 arg = wget_path+' -bqc -r nd -P \"""{0}\" --ftp-user={1} --ftp-password={2} --content-on-error {3}'.format(self.folder+"/data",ftp_user,ftp_pass,(url+datefolder+"/"+file1))
#                 arg = wget_path + " -bqc -r -nd -P \"""{0}\" ".format(self.folder+"/"+createTime_folder)+ "--ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(url+datefolder+"/"+file1)) #이건 한번에 받아오는 거라서..파일을 셀 수가 없어
            arg = wget_path + " -r -nd -P \"""{0}\" ".format(folder)+ "--ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(url+datefolder+"/"+file1)) #이건 한번에 받아오는 거라서..파일을 셀 수가 없어
            
            #실행
#             arg = wget_path + "  -r -nd -P \"""{0}\" ".format(folder+"/"+createTime_folder)+ "--ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(url+datefolder+"/"+file1))
            list.append(arg)
#                 file.write(arg+"\n")
#             arg = wget_path + " -r -nd -P /{0} -A ".format("GPM_BAT")+ "\"" +file1+"\"" + " --ftp-user=jh-kim@kict.re.kr --ftp-password=jh-kim@kict.re.kr --content-on-error {0}".format(url)
#             print arg
#         file.close()
    return list
    
# create_bat_script("2014-03-12","2014-06-11")


# CMORPH DATA DOWNLOAD
def cmorph_data_download(start,end,folder):
    output = os.getenv('USERPROFILE') + '\\Desktop\\' + "CMORPH_data_download.bat"
        
    #cmorph 3hr 0.25deg - 일단 고정
    ftp_url="ftp://ftp.cpc.ncep.noaa.gov/precip/global_CMORPH/3-hourly_025deg/"
    
    # 다운받을 데이터 날짜
    daylist = []
    days= datetime.strptime(end, "%Y-%m-%d").date() - datetime.strptime(start, "%Y-%m-%d").date()
    for i in range(days.days):
        timeday= datetime.strptime(start, "%Y-%m-%d").date()+timedelta(+i)
        daylist.append(timeday)
    
    #이미이전에 있었나요? 지우고 시작합시다.
    if os.path.exists(output):
        os.remove(output)
     
    #마지막 날짜는 따로 추가
    timeday=datetime.strptime(end, "%Y-%m-%d").date()
    daylist.append(timeday)
    file = open(output,'w+')
    list = [] ; 
    for day in daylist:
#         datefolder= day.strftime('%Y%m')
        fileName = "CMORPH+MWCOMB_3HRLY-025DEG_{0}.Z".format(str(day).replace("-", ""))
        arg = wget_path + " -r -nd -P \"""{0}\" ".format(folder+"/") + "--content-on-error {0}".format((ftp_url+fileName))
        list.append(arg)
#         arg = wget_path + " -bqc -r -nd -P \"""{0}\" ".format(folder+"/"+createTime_folder)+
#  "--ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(url+datefolder+"/"+file1))
        file.write(arg+"\n")
    
    file.close()
    return list