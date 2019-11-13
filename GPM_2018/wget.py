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
import subprocess


#제발 사용자 이름에 공백이나 한글을 좀 제거해주셨으면 하는 바램이 있어요...인식 못하는 외국언어가 많아요..
username = getpass.getuser()
wget_path = os.path.dirname(os.path.abspath(__file__))+"/Lib/wget.exe"
wget_path = wget_path.replace(username,"\""+username+"\"")
output="'"

list=[]
def ftp_filename_get(char,url,userid, userpw,start):
#     output = os.getenv('USERPROFILE') + '\\Desktop\\' + "{0}_data_download.listing".format(str(char))
    
#     print start
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
        ftp.cwd("{0}/".format((start.strftime('%Y%m'))))
 
    data=[]
         
    ftp.dir(data.append) 
    
    
#     file = open(output,'w+')
    filename=[]
    for line in data:
        if ( start.strftime("%Y%m%d") in line.split()[8]):
#             file.write(line.split()[8])
            filename.append( line.split()[8])
#             break
#         filename.append( line.split()[8])
#     file.close()
    ftp.close()
    
#     for i in filename:
#         print i
    
    return filename


# NASA GPM DATA DOWNLOAD
def create_bat_script(Id,Pw,start,end,folder):
# def create_bat_script(Id,Pw,start,end):
#     output = os.getenv('USERPROFILE') + '\\Desktop\\' + "GPM_data_download.bat"

#     ftp_user = "jh-kim@kict.re.kr"
#     ftp_pass = "jh-kim@kict.re.kr"
    ftp_user = str(Id)
    ftp_pass = str(Pw)
#     ftp_path ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/early/"
#     ftp_path ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/late/" #2018-12-26 메일에서 late 사용으로 변경됨.

#     url ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/early/"
    
    ftp_url ="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/late/" #2018-12-26 메일에서 late 사용으로 변경됨.
    url="jsimpson.pps.eosdis.nasa.gov/data/imerg/late/"
    
#     daylist = []
    start = datetime.strptime(start, "%Y-%m-%d").date()
    days= datetime.strptime(end, "%Y-%m-%d").date() - start
    
    output = os.getenv('USERPROFILE') + '\\Desktop\\' + "{0}_data_download.listing".format("gpm")
    if os.path.exists(output):
        os.remove(output)
    file_listing = open(output,'w+')
    
    for i in range(days.days+1):
#         if len(str(start.month)) == 1: 
#             month = "0"+ str(start.month) # mm 
#         else:
#             month =str(start.month)
#         https://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/CRT/0.25deg-3HLY/2011/201106/
        file= ftp_filename_get("gpm",url,ftp_user,ftp_pass,start)
        
        for filename in file:
            file_listing.write(filename+"\n")
            path = ftp_url+"{0}/".format(str(start.strftime('%Y%m')))+filename
            arg = wget_path + " -r -nd -P \"""{0}\" ".format(folder)+ "--limit-rate=20000k --ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(path))
            list.append(arg)
#             subprocess.call(arg,shell=True)
#             arg = wget_path + " -r -nd -P \"""\" "+ "--ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(url+"/"+path))
#             bat_file.write(arg+"\n")
        start = start+ timedelta(days=1)
    file_listing.close()    
    return list

    
# Id,Pw,start,end    
# create_bat_script("mhcho058@hermesys.co.kr","mhcho058@hermesys.co.kr","2019-05-22","2019-05-31","D:/Working/Gungiyeon/GPM/GPM_test/T20190723/0_download")

# CMORPH DATA DOWNLOAD
def cmorph_data_download(start,end,folder):
    output = os.getenv('USERPROFILE') + '\\Desktop\\' + "{0}_data_download.listing".format("cmorph")
# def cmorph_data_download(start,end):
#     output = os.getenv('USERPROFILE') + '\\Desktop\\' + "CMORPH_data_download.bat"
#         #이미이전에 있었나요? 지우고 시작합시다.
#     if os.path.exists(output):
#         os.remove(output)
        
    #cmorph 3hr 0.25deg - 일단 고정
    ftp_url="https://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/CRT/0.25deg-3HLY/"
    url ="ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/CRT/0.25deg-3HLY/"
    
    #============ 2019-07-15 갱신
    # 다운받을 데이터 날짜
#     daylist = []
    start=datetime.strptime(start, "%Y-%m-%d").date()
    days= datetime.strptime(end, "%Y-%m-%d").date() - start
    
    if os.path.exists(output):
        os.remove(output)
    file_listing = open(output,'w+')
    for i in range(days.days+1):
#         if len(str(start.month)) == 1: 
#             month = "0"+ str(start.month) # mm 
#         else:
#             month =str(start.month)
#         https://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/CRT/0.25deg-3HLY/2011/201106/
       
        file=  ftp_filename_get("cmorph",url,"","",start)
        
        for filename in file:
            file_listing.write(filename+"\n")
#             path = ftp_url+"{0}/{1}/".format(str(start.strftime('%Y'))), str(start.strftime('%Y%m'))+ filename
            path = ftp_url +"{0}/{1}/{2}".format(str(start.strftime('%Y')), str(start.strftime('%Y%m')),filename) 
            arg = wget_path + "  -r -nd -P \"""{0}\" ".format(folder+"/") + "--content-on-error {0}".format((path))
#             print arg
            list.append(arg)
        start = start+ timedelta(days=1)
    file_listing.close()  
    return list
#         os.system(arg)
#         subprocess.call(arg,shell=True)
#         print arg
#         arg = wget_path + " -bqc -r -nd -P \"""{0}\" ".format(folder+"/"+createTime_folder)+
#  "--ftp-user={0} --ftp-password={1} --content-on-error {2}".format(ftp_user,ftp_pass,(url+datefolder+"/"+file1))
#         file.write(arg+"\n")
    
#     file.close()
# cmorph_data_download("2018-09-30","2018-10-05")
# start =  datetime.strptime("2018-09-30", "%Y-%m-%d").date()
# end =  datetime.strptime("2018-10-05", "%Y-%m-%d").date()
# start = "2018-09-30"
# end = "2018-10-05"
# cmorph_data_download(start,end,"D:/Working/Gungiyeon/GPM/GPM_test/T20190621")