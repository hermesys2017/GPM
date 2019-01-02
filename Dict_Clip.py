# -*- coding: utf-8 -*-
'''
Created on 2018. 12. 11.

@author: MHCHO
'''

class dict_clip:
    def __init__(self):
        self.Clip_dic = {}
        
        # =========== Add CLIP zone ========================٩(ˊᗜˋ*)و
        '''
        CLIP zone의 영역 추가 시 콤보 박스에 추가할 수 있음,
        해당 파일 수정 시 반드시 플러그인 Reload 혹은 QGIS 재시작
        띄어쓰기 안됨, Dic_Clip_zone과 동일한 nameing으로 할 것.
        '''
        self.cmb_Clip =["Select Country","Korea","South_Korea","Philippines","Morocco", "Korea_Typoon","TTT"]
        
        self.Dic_Clip_zone()
    
    #clip 영역을 설정합니다. 
    def Dic_Clip_zone(self):
        # -te xmin ymin xmax ymax:

        # 한반도
        self.Clip_dic['Korea'] = '123.35 43.65 131.35 32.25'

        # 남한
        self.Clip_dic['South_Korea'] = '124.9 38.9 131.1 32.7'

        # 필리핀
        self.Clip_dic['Philippines'] = '116.9 19.4 126.6 5.0'

        # 모르코
        self.Clip_dic['Morocco'] = '-13.0 36.0 -1.0 27.0' 
        
        #koreatypoon
        self.Clip_dic['Korea_Typoon'] = '90 46 140 5'
        
        # =========== Add CLIP zone =========================
        '''
         #사용자가 CLIP 영역을 추가 할 수 있습니다.
         # 이름 입력 : 자유롭게(영어) User_CLIP 부분을 변경해서 사용
         #  영역 순서 : xMin yMax xMax yMin 로 입력
        '''
        self.Clip_dic['TTT'] = 'xMin yMax xMax yMin'
        
        