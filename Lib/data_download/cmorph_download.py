# -*- coding: utf-8 -*-
"""
Created on 2019. 12. 11.

비상용 cmorph wget download batch 파일 생성

@author: USER
"""

import os, getpass


from datetime import *

# username = getpass.getuser()
# wget_path = os.path.dirname(os.path.abspath(__file__))+"/Lib/wget.exe"
# print (wget_path)
# wget_path = wget_path.replace(username,"\""+username+"\"")


def create_cmorph_batchfile(wget_path, start, end, output):
    #     /precip/CMORPH_V1.0/CRT/0.25deg-3HLY/2018/201811/CMORPH_V1.0_ADJ_0.25deg-3HLY_20181101.bz2

    batchfile = output + "/cmorph_data_download.bat"
    create_batch = open(batchfile, "w+")

    start = datetime.strptime(start, "%Y-%m-%d").date()
    days = datetime.strptime(end, "%Y-%m-%d").date() - start
    for i in range(days.days + 1):
        url = "https://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/CRT/0.25deg-3HLY/{0}/{1}/".format(
            str(start.strftime("%Y")), str(start.strftime("%Y%m"))
        )
        # CMORPH_V1.0_ADJ_0.25deg-3HLY_20181101.bz2
        filename = "CMORPH_V1.0_ADJ_0.25deg-3HLY_{0}.bz2".format(
            str(start.strftime("%Y%m%d"))
        )

        path = url + filename
        arg = wget_path + ' -r -nd -P "' '{0}" '.format(
            output + "/CMORPH/"
        ) + "--limit-rate=20000k --content-on-error {0}".format(path)
        create_batch.write(arg + "\n")
        start = start + timedelta(days=1)

    create_batch.close()


# folder='D:/Working/KICT/Gungiyeon/GPM/GPM_test/qgisv3/T_20191206'
# create_cmorph_batchfile("2018-11-02","2018-11-03",folder)
