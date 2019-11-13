# -*- coding: utf-8 -*-

import ftplib
from datetime import datetime,timedelta
from test.test_sax import start

# def ftp_filename_get(char,url,userid, userpw,start, end):
def ftp_filename_get(char,url,userid, userpw,start):
    userid='mhcho058@hermesys.co.kr'
    userpw='mhcho058@hermesys.co.kr'
    # url = "jsimpson.pps.eosdis.nasa.gov"
#     url_c="ftp.cpc.ncep.noaa.gov"
#     print url.split("/")[0]
#     print (((str(url.split("/")[1:]).replace("', '","/"))).replace("['","")).replace("']","")
    
    print start
    if len(str(start.month)) == 1: 
        month = "0"+ str(start.month) # mm 
    else:
        month =str(start.month)
         
    ftp = ftplib.FTP(url.split("/")[0])
#     # ftp = ftplib.FTP_TLS()
#     ftp.set_debuglevel(2)
    ftp.login(userid,userpw)
       
    dir =(((str(url.split("/")[1:]).replace("', '","/"))).replace("['","")).replace("']","")
    ftp.cwd(dir)
    if (char.lower() =="cmorph"):
        ftp.cwd("{0}/{1}/".format(start.year, str(start.year)+ month))
    elif (char.lower()=="gpm"):
        ftp.cwd("{0}/".format(str(start.year)+ month))
 
    data=[]
         
    ftp.dir(data.append) 
    
    filename=[]
    for line in data:
        if ( start.strftime("%Y%m%d") in line.split()[8]):
            filename.append( line.split()[8])
#             break
#         filename.append( line.split()[8])
    ftp.close()
#     for i in filename:
#         print i
    
    return filename

ftp_url="ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/late/"
start = "2019-04-30"
end ="2019-05-01"
start= datetime.strptime(start, "%Y-%m-%d").date()
end= datetime.strptime(end, "%Y-%m-%d").date()
days= end-start

count = 0
for i in range(days.days+1):
    if len(str(start.month)) == 1: 
        month = "0"+ str(start.month) # mm 
    else:
        month =str(start.month)
    file= ftp_filename_get("GPM","jsimpson.pps.eosdis.nasa.gov/data/imerg/late/","","",start)
    for filename in file:
        print count
        print ftp_url+"{0}/".format(str(start.year)+ month)+filename
        
        count=count +1
    start = start+ timedelta(days=1)
