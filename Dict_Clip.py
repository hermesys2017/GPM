# -*- coding: utf-8 -*-
"""
Created on 2018. 12. 11.

@author: MHCHO
"""

import os

# import configparser
# filePath = os.path.dirname(os.path.abspath(__file__))+"/Lib/reference/clip_zone.ini"


class dict_clip:
    def __init__(self):
        self.Clip_dic = {}

        # =========== Add CLIP zone ========================٩(ˊᗜˋ*)و
        """
        CLIP zone의 영역 추가 시 콤보 박스에 추가할 수 있음,
        해당 파일 수정 시 반드시 플러그인 Reload 혹은 QGIS 재시작
        띄어쓰기 안됨, Dic_Clip_zone과 동일한 nameing으로 할 것.
        
        """
        self.cmb_Clip = [
            "Select Country",
            "Korea",
            "South_Korea",
            "North_Korea",
            "Philippines",
            "Morocco",
            "Korea_Typoon",
            "Test1",
        ]

        # 2021.11.05 JO : utm 좌표계 설정 이쪽으로 이동
        self.cmb_utm = [
            "Select UTM",
            "WGS84_UTM 1N",
            "WGS84_UTM 1S",
            "WGS84_UTM 2N",
            "WGS84_UTM 2S",
            "WGS84_UTM 3N",
            "WGS84_UTM 3S",
            "WGS84_UTM 4N",
            "WGS84_UTM 4S",
            "WGS84_UTM 5N",
            "WGS84_UTM 5S",
            "WGS84_UTM 6N",
            "WGS84_UTM 6S",
            "WGS84_UTM 7N",
            "WGS84_UTM 7S",
            "WGS84_UTM 8N",
            "WGS84_UTM 8S",
            "WGS84_UTM 9N",
            "WGS84_UTM 9S",
            "WGS84_UTM 10S",
            "WGS84_UTM 11N",
            "WGS84_UTM 11S",
            "WGS84_UTM 12N",
            "WGS84_UTM 12S",
            "WGS84_UTM 13N",
            "WGS84_UTM 13S",
            "WGS84_UTM 14N",
            "WGS84_UTM 14S",
            "WGS84_UTM 15N",
            "WGS84_UTM 15S",
            "WGS84_UTM 16N",
            "WGS84_UTM 16S",
            "WGS84_UTM 17N",
            "WGS84_UTM 17S",
            "WGS84_UTM 18N",
            "WGS84_UTM 18S",
            "WGS84_UTM 19N",
            "WGS84_UTM 19S",
            "WGS84_UTM 20N",
            "WGS84_UTM 20S",
            "WGS84_UTM 21N",
            "WGS84_UTM 21S",
            "WGS84_UTM 22N",
            "WGS84_UTM 22S",
            "WGS84_UTM 23N",
            "WGS84_UTM 23S",
            "WGS84_UTM 24N",
            "WGS84_UTM 24S",
            "WGS84_UTM 25N",
            "WGS84_UTM 25S",
            "WGS84_UTM 26N",
            "WGS84_UTM 26S",
            "WGS84_UTM 27N",
            "WGS84_UTM 27S",
            "WGS84_UTM 28N",
            "WGS84_UTM 28S",
            "WGS84_UTM 29N",
            "WGS84_UTM 29S",
            "WGS84_UTM 30N",
            "WGS84_UTM 30S",
            "WGS84_UTM 31N",
            "WGS84_UTM 31S",
            "WGS84_UTM 32N",
            "WGS84_UTM 32S",
            "WGS84_UTM 33N",
            "WGS84_UTM 33S",
            "WGS84_UTM 34N",
            "WGS84_UTM 34S",
            "WGS84_UTM 35N",
            "WGS84_UTM 35S",
            "WGS84_UTM 36N",
            "WGS84_UTM 36S",
            "WGS84_UTM 37N",
            "WGS84_UTM 37S",
            "WGS84_UTM 38N",
            "WGS84_UTM 38S",
            "WGS84_UTM 39N",
            "WGS84_UTM 39S",
            "WGS84_UTM 40N",
            "WGS84_UTM 40S",
            "WGS84_UTM 41N",
            "WGS84_UTM 41S",
            "WGS84_UTM 42N",
            "WGS84_UTM 42S",
            "WGS84_UTM 43N",
            "WGS84_UTM 43S",
            "WGS84_UTM 44N",
            "WGS84_UTM 44S",
            "WGS84_UTM 45N",
            "WGS84_UTM 45S",
            "WGS84_UTM 46N",
            "WGS84_UTM 46S",
            "WGS84_UTM 47N",
            "WGS84_UTM 47S",
            "WGS84_UTM 48N",
            "WGS84_UTM 48S",
            "WGS84_UTM 49N",
            "WGS84_UTM 49S",
            "WGS84_UTM 50N",
            "WGS84_UTM 50S",
            "WGS84_UTM 51N",
            "WGS84_UTM 51S",
            "WGS84_UTM 52N",
            "WGS84_UTM 52S",
            "WGS84_UTM 53N",
            "WGS84_UTM 53S",
            "WGS84_UTM 54N",
            "WGS84_UTM 54S",
            "WGS84_UTM 55N",
            "WGS84_UTM 55S",
            "WGS84_UTM 56N",
            "WGS84_UTM 56S",
            "WGS84_UTM 57N",
            "WGS84_UTM 57S",
            "WGS84_UTM 58N",
            "WGS84_UTM 58S",
            "WGS84_UTM 59N",
            "WGS84_UTM 59S",
            "WGS84_UTM 60N",
            "WGS84_UTM 60S",
        ]

        self.Dic_Clip_zone()

    # clip 영역을 설정합니다.
    def Dic_Clip_zone(self):
        # -te xmin ymin xmax ymax:

        # 한반도
        #         self.Clip_dic['Korea'] = '123.35 43.65 131.35 32.25'
        self.Clip_dic[
            "Korea"
        ] = "122.7373493269162594 44.4776569326958224 132.8373493269162680 32.5776569326958239"

        # 남한
        self.Clip_dic["South_Korea"] = "124.9 38.9 131.1 32.7"

        # 북한-2019-07-11  신설
        self.Clip_dic[
            "North_Korea"
        ] = "123.2368153680681218 44.0661887319925114 131.5368153680681189 37.6661887319925128"

        # 필리핀
        self.Clip_dic["Philippines"] = "116.9 19.4 126.6 5.0"

        # 모르코
        self.Clip_dic["Morocco"] = "-13.0 36.0 -1.0 27.0"

        # koreatypoon
        self.Clip_dic["Korea_Typoon"] = "90 46 140 5"

        # =========== Add CLIP zone =========================
        """
         #사용자가 CLIP 영역을 추가 할 수 있습니다.
         # 이름 입력 : 자유롭게(영어) User_CLIP 부분을 변경해서 사용
         #  영역 순서 : xMin yMax xMax yMin 로 입력
        """
        self.Clip_dic["Test1"] = "xMin yMax xMax yMin"


#         self.Clip_dic['TTT'] = '90 46 120 6'
