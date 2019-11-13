# -*- coding: utf-8 -*-
'''
Created on 2018. 10. 2.

@author: MH.CHO
'''
import sys,time
import GPM

# from PyQt4.QtGui import QProgressDialog, QProgressBar
# 
# def progdialog(progress):
#     dialog = QProgressDialog()
#     dialog.setWindowTitle("Progress")
#     dialog.setLabelText("text")
#     bar = QProgressBar(dialog)
#     bar.setTextVisible(True)
#     bar.setValue(progress)
#     dialog.setBar(bar)
#     dialog.setMinimumWidth(300)
#     dialog.show()
#     return dialog, bar
# 
# def calc(x, y):
#     dialog, bar = progdialog(0)
#     bar.setValue(0)
#     bar.setMaximum(100)
#     sum = 0
#     progress = 0
#     for i in range(x):
#         for j in range(y):
#             k = i + j
#             sum += k
#         i += 1
#         progress = (float(i) / float(x)) * 100
#         bar.setValue(progress)

def progressbar(it, prefix="", size=60):
    count = len(it)
    def _show(_i):
        x = int(size*_i/count)
#         print prefix,"#"*x,"."*(size-x),_i,count
        sys.stdout.write("{0} [{1} {2}] {3}/{4} ".format(prefix,"#"*x,"."*(size-x),_i,count))
#         sys.stdout.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), _i, count))
        sys.stdout.flush()

#     _show(0)
    for i, item in enumerate(it):
        yield item
#         _show(i+1)
    _show(i+1)
    sys.stdout.write("\n")
    sys.stdout.flush()
    
def run(size):
    for i in progressbar(range(size), "Progress: ", 30):
        time.sleep(0.01) # any calculation you need

def qgis_progressBar(progress,list):
    #------ list == size 임.
    count = 0
    for count in range((list)):
        count= count +1
        #진행률 바 생성
        progressMessageBar = GPM._iface.messageBar().createMessage(("Progress rate  "))
        progressMessageBar.layout().addWidget(progress)
        GPM._iface.messageBar().pushWidget(progressMessageBar, GPM._iface.messageBar().SUCCESS)
        progress.setMaximum(list)
         
        #진행률 % 표현
        progress.setValue(count)

#     #진행률 바가 100%가 되면 자동으로 메세지 바 삭제
#     GPM._iface.messageBar().clearWidgets()
