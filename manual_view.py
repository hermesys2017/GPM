# -*- coding: utf-8 -*-
'''
Created on 2019. 5.2

@author: MHCHO
'''

import os

from PyQt4 import *
# from PyQt4 import QtGui, uic
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView


path = os.path.dirname(os.path.realpath(__file__))
settings_icon = path + '\image\settings.png'
FORM_CLASS, _ = uic.loadUiType(os.path.join(
os.path.dirname(__file__), 'manual_webview.ui'))

class manual_webview(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(manual_webview, self).__init__(parent)
        self.setupUi(self)
        
#         self.set_webManual()
        
        self.Set_treeWidget()
    
#     def open_new_dialog(self):
#         self.nd = manual_webview(self)
#         self.nd.show()
    
#     def set_webManual(self):
#         myWV = self.webView(None);
# #         myWV = QWebView(None)
#         myWV.load(QUrl("http://www.google.co.kr"));
#         myWV.show()
    
    def Set_treeWidget(self):
        self.treeWidget.setHeaderHidden(True)
        item0= QtGui.QTreeWidgetItem(self.treeWidget, ['Data Download'])
        icon = QtGui.QIcon(settings_icon)
        item0.setIcon(0, icon)
        item1 = QtGui.QTreeWidgetItem(self.treeWidget, ['HDF5_Convert'])
        icon = QtGui.QIcon(settings_icon)
        item1.setIcon(0, icon)
        
#         self.mainLayout = QtGui.QGridLayout(self)
#         self.mainLayout.addWidget(self.treeWidget)
#         self.treeWidget.itemDoubleClicked.connect(self.OnDoubleClick)
        
    # �޴� Ʈ�� ��Ͽ��� ������ Ŭ�������� �̺�Ʈ ó��
    def OnDoubleClick(self, item):
        try:
            SelectItme = item.text(0)
            if SelectItme == 'Data Download':
                myWV = self.webView(None);
                myWV.load(QUrl("http://www.naver.com"));
                myWV.show()
#                 self.tabWidget.setCurrentIndex(1)
#             if SelectItme == 'Clip':
#                 self.tabWidget.setCurrentIndex(2)
#             elif SelectItme == "UTM":
#                 self.tabWidget.setCurrentIndex(3)
#             elif SelectItme == "Resampling":
#                 self.tabWidget.setCurrentIndex(4)
#             elif SelectItme == "Accum":
#                 self.tabWidget.setCurrentIndex(5)
#             elif SelectItme == 'Make CSV':
#                 self.tabWidget.setCurrentIndex(6)
#             elif SelectItme == 'Function':
#                 self.tabWidget.setCurrentIndex(7)
#             elif SelectItme == 'Make ASC':
#                 self.tabWidget.setCurrentIndex(8)
#             elif SelectItme == 'Satellitecorrection':
#                 self.tabWidget.setCurrentIndex(9)
#             elif SelectItme == 'Make Image':
#                 self.tabWidget.setCurrentIndex(10)
#             elif SelectItme == 'Data Download':
#                 self.tabWidget.setCurrentIndex(0)
#             elif SelectItme == 'Help':
#                 self.manual_open()
# #                 self.tabWidget.setCurrentIndex(11)
 
        except Exception as es:
            _util.MessageboxShowError("Error message", str(es))

#     def manual_webviewer(self,url):
#         myWV = self.QWebView(None);
#         myWV.load(QUrl(url));
#         myWV.show()