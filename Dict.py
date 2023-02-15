# -*- coding: utf-8 -*-
import sys
import os
import os.path


class dict:
    def __init__(self):
        self.UTM_dic = {}
#         self.Clip_dic = {}

        self.Dic_UTM()
#         self.Dic_Clip()

    def Dic_UTM(self):
        self.UTM_dic['WGS84_UTM 1N'] ='+proj=utm +zone=1 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 1S'] ='+proj=utm +zone=1 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 2N'] ='+proj=utm +zone=2 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 2S'] ='+proj=utm +zone=2 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 3N'] ='+proj=utm +zone=3 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 3S'] ='+proj=utm +zone=3 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 4N'] ='+proj=utm +zone=4 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 4S'] ='+proj=utm +zone=4 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 5N'] ='+proj=utm +zone=5 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 5S'] ='+proj=utm +zone=5 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 6N'] ='+proj=utm +zone=6 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 6S'] ='+proj=utm +zone=6 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 7N'] ='+proj=utm +zone=7 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 7S'] ='+proj=utm +zone=7 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 8N'] ='+proj=utm +zone=8 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 8S'] ='+proj=utm +zone=8 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 9N'] ='+proj=utm +zone=9 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 9S'] ='+proj=utm +zone=9 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 10N'] ='+proj=utm +zone=10 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 10S'] ='+proj=utm +zone=10 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 11N'] ='+proj=utm +zone=11 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 11S'] ='+proj=utm +zone=11 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 12N'] ='+proj=utm +zone=12 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 12S'] ='+proj=utm +zone=12 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 13N'] ='+proj=utm +zone=13 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 13S'] ='+proj=utm +zone=13 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 14N'] ='+proj=utm +zone=14 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 14S'] ='+proj=utm +zone=14 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 15N'] ='+proj=utm +zone=15 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 15S'] ='+proj=utm +zone=15 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 16N'] ='+proj=utm +zone=16 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 16S'] ='+proj=utm +zone=16 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 17N'] ='+proj=utm +zone=17 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 17S'] ='+proj=utm +zone=17 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 18N'] ='+proj=utm +zone=18 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 18S'] ='+proj=utm +zone=18 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 19N'] ='+proj=utm +zone=19 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 19S'] ='+proj=utm +zone=19 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 20N'] ='+proj=utm +zone=20 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 20S'] ='+proj=utm +zone=20 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 21N'] ='+proj=utm +zone=21 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 21S'] ='+proj=utm +zone=21 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 22N'] ='+proj=utm +zone=22 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 22S'] ='+proj=utm +zone=22 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 23N'] ='+proj=utm +zone=23 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 23S'] ='+proj=utm +zone=23 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 24N'] ='+proj=utm +zone=24 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 24S'] ='+proj=utm +zone=24 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 25N'] ='+proj=utm +zone=25 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 25S'] ='+proj=utm +zone=25 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 26N'] ='+proj=utm +zone=26 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 26S'] ='+proj=utm +zone=26 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 27N'] ='+proj=utm +zone=27 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 27S'] ='+proj=utm +zone=27 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 28N'] ='+proj=utm +zone=28 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 28S'] ='+proj=utm +zone=28 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 29N'] ='+proj=utm +zone=29 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 29S'] ='+proj=utm +zone=29 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 30N'] ='+proj=utm +zone=30 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 30S'] ='+proj=utm +zone=30 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 31N'] ='+proj=utm +zone=31 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 31S'] ='+proj=utm +zone=31 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 32N'] ='+proj=utm +zone=32 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 32S'] ='+proj=utm +zone=32 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 33N'] ='+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 33S'] ='+proj=utm +zone=33 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 34N'] ='+proj=utm +zone=34 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 34S'] ='+proj=utm +zone=34 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 35N'] ='+proj=utm +zone=35 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 35S'] ='+proj=utm +zone=35 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 36N'] ='+proj=utm +zone=36 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 36S'] ='+proj=utm +zone=36 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 37N'] ='+proj=utm +zone=37 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 37S'] ='+proj=utm +zone=37 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 38N'] ='+proj=utm +zone=38 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 38S'] ='+proj=utm +zone=38 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 39N'] ='+proj=utm +zone=39 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 39S'] ='+proj=utm +zone=39 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 40N'] ='+proj=utm +zone=40 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 40S'] ='+proj=utm +zone=40 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 41N'] ='+proj=utm +zone=41 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 41S'] ='+proj=utm +zone=41 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 42N'] ='+proj=utm +zone=42 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 42S'] ='+proj=utm +zone=42 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 43N'] ='+proj=utm +zone=43 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 43S'] ='+proj=utm +zone=43 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 44N'] ='+proj=utm +zone=44 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 44S'] ='+proj=utm +zone=44 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 45N'] ='+proj=utm +zone=45 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 45S'] ='+proj=utm +zone=45 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 46N'] ='+proj=utm +zone=46 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 46S'] ='+proj=utm +zone=46 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 47N'] ='+proj=utm +zone=47 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 47S'] ='+proj=utm +zone=47 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 48N'] ='+proj=utm +zone=48 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 48S'] ='+proj=utm +zone=48 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 49N'] ='+proj=utm +zone=49 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 49S'] ='+proj=utm +zone=49 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 50N'] ='+proj=utm +zone=50 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 50S'] ='+proj=utm +zone=50 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 51N'] ='+proj=utm +zone=51 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 51S'] ='+proj=utm +zone=51 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 52N'] ='+proj=utm +zone=52 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 52S'] ='+proj=utm +zone=52 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 53N'] ='+proj=utm +zone=53 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 53S'] ='+proj=utm +zone=53 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 54N'] ='+proj=utm +zone=54 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 54S'] ='+proj=utm +zone=54 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 55N'] ='+proj=utm +zone=55 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 55S'] ='+proj=utm +zone=55 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 56N'] ='+proj=utm +zone=56 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 56S'] ='+proj=utm +zone=56 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 57N'] ='+proj=utm +zone=57 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 57S'] ='+proj=utm +zone=57 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 58N'] ='+proj=utm +zone=58 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 58S'] ='+proj=utm +zone=58 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 59N'] ='+proj=utm +zone=59 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 59S'] ='+proj=utm +zone=59 +south +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 60N'] ='+proj=utm +zone=60 +datum=WGS84 +units=m +no_defs'
        self.UTM_dic['WGS84_UTM 60S'] ='+proj=utm +zone=60 +south +datum=WGS84 +units=m +no_defs'
        
        
        
        
#         self.UTM_dic['WGS84_UTM 27N'] = '+proj=utm +zone=27 +datum=WGS84 +units=m +no_defs'
#         self.UTM_dic['WGS84_UTM 28N'] = '+proj=utm +zone=28 +datum=WGS84 +units=m +no_defs'
#         self.UTM_dic['WGS84_UTM 29N'] = '+proj=utm +zone=29 +datum=WGS84 +units=m +no_defs'
#         self.UTM_dic['WGS84_UTM 30N'] = '+proj=utm +zone=30 +datum=WGS84 +units=m +no_defs'
#         self.UTM_dic['WGS84_UTM 50N'] = '+proj=utm +zone=50 +datum=WGS84 +units=m +no_defs'
#         self.UTM_dic['WGS84_UTM 51N'] = '+proj=utm +zone=51 +south +datum=WGS84 +units=m +no_defs'
#         self.UTM_dic['WGS84_UTM 52N'] = '+proj=utm +zone=52 +datum=WGS84 +units=m +no_defs'
#         self.UTM_dic['WGS84_UTM 53N'] = '+proj=utm +zone=53 +datum=WGS84 +units=m +no_defs'

#     def Dic_Clip(self):
#         # -te xmin ymin xmax ymax:
# 
#         # 한반도
#         # originalGrid.ProjToCell(123.35, 32.25, out intC1, out intR1);
#         # originalGrid.ProjToCell(131.35, 43.65, out intC2, out intR2);
# #         self.Clip_dic['Korea'] = '123.35 32.25 131.35 43.65' #clipper 기능을 사용할 때 보니 좌표 순서의 문제가 있음.
#         self.Clip_dic['Korea'] = '123.35 43.65 131.35 32.25'
# 
#         # 남한
#         # originalGrid.ProjToCell(124.9, 32.7, out intC1, out intR1);
#         # originalGrid.ProjToCell(131.1, 38.9, out intC2, out intR2);
# #         self.Clip_dic['South Korea'] = '124.9 32.7 131.1 38.9'
#         self.Clip_dic['South_Korea'] = '124.9 38.9 131.1 32.7'
# 
#         # 필리핀
#         #  originalGrid.ProjToCell(116.9, 5.0, out intC1, out intR1);
#         #  originalGrid.ProjToCell(126.6, 19.4, out intC2, out intR2);
# #         self.Clip_dic['Philippines'] = '116.9 5.0 126.6, 19.4'
#         self.Clip_dic['Philippines'] = '116.9 19.4 126.6 5.0'
# 
#         # 모르코
#         # originalGrid.ProjToCell(-13.0, 27.0, out intC1, out intR1);
#         # originalGrid.ProjToCell(-1.0, 36.0, out intC2, out intR2);
# #         self.Clip_dic['Morocco'] = '-13.0 27.0 -1.0 36.0'
#         self.Clip_dic['Morocco'] = '-13.0 36.0 -1.0 27.0' 
#         
#         #koreatypoon
#         self.Clip_dic['Korea_Typoon'] = '90 46 140 5'
        
        
