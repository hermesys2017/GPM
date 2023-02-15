# -*- coding: utf-8 -*-
"""
Created on 2019. 5.2

@author: MHCHO
"""

import os

from PyQt5 import *

# # from PyQt4 import QtGui, uic
# # from PyQt5.QtCore import QUrl
# # from PyQt5.QtWebKitWidgets import QWebPage
# # from PyQt5.QtWebKitWidgets import QWebView
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *
# from PyQt5.QtWidgets import *

import PyQt5
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtNetwork import *
import sys
from optparse import OptionParser

path = os.path.dirname(os.path.realpath(__file__))
settings_icon = path + "\image\settings.png"
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "manual_webview.ui")
)


# class MyBrowser(QWebPage):
#     ''' Settings for the browser.'''
#
#     def userAgentForUrl(self, url):
#         ''' Returns a User Agent that will be seen by the website. '''
#         return "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"


class Browser(QWebView):
    def __init__(self):
        # QWebView
        self.view = QWebView.__init__(self)
        # self.view.setPage(MyBrowser())
        self.setWindowTitle("Loading...")
        self.titleChanged.connect(self.adjustTitle)
        # super(Browser).connect(self.ui.webView,QtCore.SIGNAL("titleChanged (const QString&amp;)"), self.adjustTitle)

    def load(self, url):
        self.setUrl(QUrl(url))

    def adjustTitle(self):
        self.setWindowTitle(self.title())

    def disableJS(self):
        settings = QWebSettings.globalSettings()
        settings.setAttribute(QWebSettings.JavascriptEnabled, False)


app = QApplication(sys.argv)
view = Browser()
view.showMaximized()
view.load("https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=김동희")
app.exec_()


# class manual_webview(QtWidgets.QDialog, FORM_CLASS):
#     def __init__(self, parent=None):
#         """Constructor."""
#         super(manual_webview, self).__init__(parent)
#         self.setupUi(self)
#
# #         self.set_webManual()
#
#         self.Set_treeWidget()
#
# #     def open_new_dialog(self):
# #         self.nd = manual_webview(self)
# #         self.nd.show()
#
# #     def set_webManual(self):
# # #         myWV = self.webView(None);
# #         myWV = QWebView(None)
# #         myWV.load(QUrl("http://www.google.co.kr"));
# #         myWV.show()
#
#     def Set_treeWidget(self):
#         self.treeWidget.setHeaderHidden(True)
#         item0= QTreeWidgetItem(self.treeWidget, ['Data_Download'])
#         icon = QIcon(settings_icon)
#         item0.setIcon(0, icon)
#         item1 = QTreeWidgetItem(self.treeWidget, ['HDF5_Convert'])
#         icon = QIcon(settings_icon)
#         item1.setIcon(0, icon)
#
# #         self.mainLayout = QtGui.QGridLayout(self)
# #         self.mainLayout.addWidget(self.treeWidget)
#         self.treeWidget.itemDoubleClicked.connect(self.OnDoubleClick)
# #
# #     # �޴� Ʈ�� ��Ͽ��� ������ Ŭ�������� �̺�Ʈ ó��
#     def OnDoubleClick(self, item):
#         try:
#             SelectItme = item.text(0)
#             if SelectItme == 'Data_Download':
#                 app = QApplication(sys.argv)
#                 view = Browser()
# #                 view.showMaximized()
#                 view.showMaximized()
#                 view.load("http://210.92.123.135/windy_hermesys.html")
#                 app.exec_()
# #                 myWV = self.webView(None);
# #                 myWV.load(QUrl("http://www.naver.com"));
# #                 myWV.show()
# #                 self.tabWidget.setCurrentIndex(1)
# #             if SelectItme == 'Clip':
# #                 self.tabWidget.setCurrentIndex(2)
# #             elif SelectItme == "UTM":
# #                 self.tabWidget.setCurrentIndex(3)
# #             elif SelectItme == "Resampling":
# #                 self.tabWidget.setCurrentIndex(4)
# #             elif SelectItme == "Accum":
# #                 self.tabWidget.setCurrentIndex(5)
# #             elif SelectItme == 'Make CSV':
# #                 self.tabWidget.setCurrentIndex(6)
# #             elif SelectItme == 'Function':
# #                 self.tabWidget.setCurrentIndex(7)
# #             elif SelectItme == 'Make ASC':
# #                 self.tabWidget.setCurrentIndex(8)
# #             elif SelectItme == 'Satellitecorrection':
# #                 self.tabWidget.setCurrentIndex(9)
# #             elif SelectItme == 'Make Image':
# #                 self.tabWidget.setCurrentIndex(10)
# #             elif SelectItme == 'Data Download':
# #                 self.tabWidget.setCurrentIndex(0)
# #             elif SelectItme == 'Help':
# #                 self.manual_open()
# # #                 self.tabWidget.setCurrentIndex(11)
#
#         except Exception as es:
#             print (es)
# #             _util.MessageboxShowError("Error message", str(es))
# #
# # #     def manual_webviewer(self,url):
# # #         myWV = self.QWebView(None);
# # #         myWV.load(QUrl(url));
# # #         myWV.show()
