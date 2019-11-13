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
import ftplib
import re
import subprocess


#제발 사용자 이름에 공백이나 한글을 좀 제거해주셨으면 하는 바램이 있어요...인식 못하는 외국언어가 많아요..
username = getpass.getuser()
wget_path = os.path.dirname(os.path.abspath(__file__))+"/Lib/wget.exe"
wget_path = wget_path.replace(username,"\""+username+"\"")
output="'"



#폴더 생성
def folder_create(path):
    if os.path.exists(path) == False:      
        os.mkdir(path)

def ftp_filename_get(char,url,userid, userpw,start,fileFormat):
#     output = os.getenv('USERPROFILE') + '\\Desktop\\' + "{0}_data_download.listing".format(str(char))
#     print start]
    ftp = ftplib.FTP(url.split("/")[0])
#     # ftp = ftplib.FTP_TLS()
#     ftp.set_debuglevel(2)
    ftp.login(userid,userpw)
       
    dir =(((str(url.split("/")[1:]).replace("', '","/"))).replace("['","")).replace("']","")
    ftp.cwd(dir)
    if (char.lower() =="cmorph"):
        
#         print "{0}/{1}/".format(str(start.strftime('%Y')), str(start.strftime('%Y%m')))
        ftp.cwd("{0}/{1}/".format(str(start.strftime('%Y')), str(start.strftime('%Y%m'))))
#         ftp.cwd("{0}/{1}/".format("{0}/{1}/".format(str(start.strftime('%Y'))), str(start.strftime('%Y%m'))))
    elif (char.lower()=="gpm"):
        #HDF5
        ftp.cwd("{0}/".format((start.strftime('%Y%m'))))
        #TIFF
#         ftp.cwd("{0}/{1}/".format(str(start.strftime('%Y')),str(start.strftime('%m'))))
    elif (char.lower()=="gsmap"):
        ftp.cwd("{0}/{1}/{2}/".format(str(start.strftime('%Y')), str(start.strftime('%m')),str(start.strftime('%d'))))
            
 
    data=[]
         
    ftp.dir(data.append) 
    
    
#     file = open(output,'w+')
    filename=[]
    for line in data:
        if ( start.strftime("%Y%m%d") in line.split()[8]):
            if (fileFormat == "tif" ):  
                if ("30min.tif" in line.split()[8]):
                    filename.append( line.split()[8])
            else:
#             file.write(line.split()[8])
                #CMORPH, HDF5는 이거 사용함
                filename.append( line.split()[8])
#             break
#         filename.append( line.split()[8])
#     file.close()
    ftp.close()
    
#     for i in filename:
#         print i
    
    return filename


# NASA GPM DATA DOWNLOAD
def create_bat_script(Id,Pw,start,end,folder,fileFormat):
# def create_bat_script(Id,Pw,start,end):
#     output = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_data_download.bat"
#     ftp_user = "jh-kim@kict.re.kr"
#     ftp_pass = "jh-kim@kict.re.kr"
    ftp_user = str(Id)
    ftp_pass = str(Pw)
    
    # ==================
    ftp_url ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/late/" #2018-12-26 메일에서 late 사용으로 변경됨.
    url="jsimpson.pps.eosdis.nasa.gov/data/imerg/late/"
    
    # ==================
    list=[]
    arg=""
#     daylist = []
    start = datetime.strptime(start, "%Y-%m-%d").date()
    days= datetime.strptime(end, "%Y-%m-%d").date() - start
    
#     output = os.getenv('USERPROFILE') + '\\Desktop\\' + "{0}_data_download.listing".format("gpm")
    #박사님이 뭐 다운로드 됐는지 리스트 보고 싶다 하심.
    output =folder+"/{0}_data_download.listing".format("gpm")
    if os.path.exists(output):
        os.remove(output)
    file_listing = open(output,'w+')
    
    for i in range(days.days+1):
#         if len(str(start.month)) == 1: 
#             month = "0"+ str(start.month) # mm 
#         else:
#             month =str(start.month)
#         https://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/CRT/0.25deg-3HLY/2011/201106/
        file= ftp_filename_get("gpm",url,ftp_user,ftp_pass,start,fileFormat)
        
        for filename in file:
            file_listing.write(filename+"\n")
#             #=============
            path = ftp_url+"{0}/".format(str(start.strftime('%Y%m')))+filename
            if os.path.exists(folder+"/GPM/"+filename):
                pass
            else:
                arg = wget_path + " -r -nd -P \"""{0}\" ".format(folder+"/GPM/")+ "--limit-rate=20000k --ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(path))
                list.append(arg)

        start = start+ timedelta(days=1)
    file_listing.close()    
    return list

    
# Id,Pw,start,end    
# create_bat_script("mhcho058@hermesys.co.kr","mhcho058@hermesys.co.kr","2019-05-22","2019-05-31","D:/Working/Gungiyeon/GPM/GPM_test/T20190723/0_download")

# CMORPH DATA DOWNLOAD
def cmorph_data_download(start,end,folder,fileFormat):
#     output = os.getenv('USERPROFILE') + '\\Desktop\\' + "{0}_data_download.listing".format("cmorph")
    output= folder+"/{0}_data_download.listing".format("cmorph")
        
    #cmorph 3hr 0.25deg - 일단 고정
    ftp_url="https://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/CRT/0.25deg-3HLY/"
    url ="ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/CRT/0.25deg-3HLY/"

    list=[]
    arg=""
    
    start=datetime.strptime(start, "%Y-%m-%d").date()
    days= datetime.strptime(end, "%Y-%m-%d").date() - start
    
    if os.path.exists(output):
        os.remove(output)
        
    file_listing = open(output,'w+')
    for i in range(days.days+1):
       
        file=  ftp_filename_get("cmorph",url,"","",start,fileFormat)
        
        for filename in file:
            file_listing.write(filename+"\n")
#             path = ftp_url+"{0}/{1}/".format(str(start.strftime('%Y'))), str(start.strftime('%Y%m'))+ filename
            path = ftp_url +"{0}/{1}/{2}".format(str(start.strftime('%Y')), str(start.strftime('%Y%m')),filename) 
            if os.path.exists(folder+"/CMORPH/"+filename):
                pass
            else:
                arg = wget_path + " -r -nd -P \"""{0}\" ".format(folder+"/CMORPH/") + " --limit-rate=20000k --content-on-error {0}".format((path))
#             print arg
            list.append(arg)
        start = start+ timedelta(days=1)
    file_listing.close()  
    return list

#GSMap DATA DOWNLOAD
def GSMap_data_download(Id,Pw,start,end,folder,fileformat):
    ftp_url='ftp://{0}:{1}@hokusai.eorc.jaxa.jp/standard/v6/hourly/'.format(Id,Pw)
    url='hokusai.eorc.jaxa.jp/standard/v6/hourly/'
    list=[]
    arg=""
    
    start=datetime.strptime(start, "%Y-%m-%d").date()
    days= datetime.strptime(end, "%Y-%m-%d").date() - start
    
    output =folder+"/{0}_data_download.listing".format("GSMap")
    file_listing = open(output,'w+')
    for i in range(days.days+1):
        
        file=  ftp_filename_get("gsmap",url,Id,Pw,start,fileformat)
        for filename in file:
            file_listing.write(filename+"\n")
            path = ftp_url +"{0}/{1}/{2}/{3}".format(str(start.strftime('%Y')), str(start.strftime('%m')),str(start.strftime('%d')),filename)
            if os.path.exists(folder+"/GSMap/"+filename):
                pass
            else:
                arg=wget_path+" -r -nd -P \"""{0}\" ".format(folder+"/GSMap/")+ "--limit-rate=20000k {0}".format(path)
            
            list.append(arg)
#                 print (arg)
#                 os.system(arg)
        start = start+ timedelta(days=1)
    file_listing.close()
    return list
#             

# folder='D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191028/0_DataDown/GSMap'
# GSMap_data_download("rainmap","Niskur+1404","2019-09-30","2019-10-02",folder,"")
# cmorph_data_download("2018-09-30","2018-10-05")
# start =  datetime.strptime("2018-09-30", "%Y-%m-%d").date()
# end =  datetime.strptime("2018-10-05", "%Y-%m-%d").date()
# start = "2018-09-30"
# end = "2018-10-05"
# cmorph_data_download(start,end,folder,"")