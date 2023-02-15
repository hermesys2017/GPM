# -*- coding: utf-8 -*-
import sys
import subprocess
import os, re
from datetime import datetime, timedelta
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


wget_path = (
    '"'
    + os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    + "/wget.exe"
    + '"'
)
kst_list = []


class GPM_download_Class:
    def __init__(
        self,
        userpass,
        userInfo,
        getFiledate_1,
        getFiledate_2,
        gpm_type,
        donwload_folder,
        timeLabel_type,
        progressbar,
    ):
        self.url = "https://jsimpsonhttps.pps.eosdis.nasa.gov/text"
        self.userInfo = userInfo
        self.getFiledate_1 = getFiledate_1
        self.gpm_type = gpm_type
        self.donwload_folder = donwload_folder
        self.timeLabel_type = timeLabel_type.upper()
        self.days = 0
        self.getFiledate = ""
        self.userpass = userpass
        self.progressbar = progressbar
        # kst 단위

        if self.timeLabel_type == "KST":
            if getFiledate_1 == getFiledate_2:
                self.days = 0
            else:
                self.days = str(
                    (datetime.strptime(getFiledate_2, "%Y-%m-%d").date())
                    - (datetime.strptime(getFiledate_1, "%Y-%m-%d").date())
                ).split(" ")[0]

            for day in range(int(self.days) + 2):
                self.getFiledate = str(
                    datetime.strptime(getFiledate_1, "%Y-%m-%d").date() + timedelta(day)
                )
                self.main()

        # UTC 단위
        file_list = []
        if self.timeLabel_type == "UTC":
            if getFiledate_1 == getFiledate_2:
                self.days = 0
            else:
                self.days = str(
                    (datetime.strptime(getFiledate_2, "%Y-%m-%d").date())
                    - (datetime.strptime(getFiledate_1, "%Y-%m-%d").date())
                ).split(" ")[0]

            for day in range(int(self.days) + 1):
                self.getFiledate = str(
                    datetime.strptime(getFiledate_1, "%Y-%m-%d").date() + timedelta(day)
                )
                self.year, self.month, self.day = self.getFiledate.split("-")
                file_list = file_list + self.get_file_list()
            self.main(file_list)

    def main(self, file_list):
        # self.year, self.month,self.day = self.getFiledate.split('-')
        # file_list = self.get_file_list()
        count = 0
        tiff_list = []

        if self.gpm_type == "imerg/gis" or self.gpm_type == "imerg/gis/early":
            for filename in file_list:
                if os.path.splitext(filename)[1] == ".tif":
                    if (("30min") in filename) == True:
                        tiff_list.append(filename)

            self.progressbar.setMaximum(len(tiff_list) - 1)
            QApplication.processEvents()
            for filename in tiff_list:
                if self.timeLabel_type == "UTC":
                    print("UTC")
                    self.progressbar.setValue(count)
                    self.get_file(filename)
                    count = count + 1
                    QApplication.processEvents()
            QMessageBox.information(
                None,
                "GPM Download ",
                " Download is complete. Please check the download folder",
            )

        if self.gpm_type == "imerg/late" or self.gpm_type == "imerg/early":
            self.progressbar.setMaximum(len(file_list) - 1)
            QApplication.processEvents()
            for filename in file_list:
                if self.timeLabel_type == "UTC":
                    self.get_file(filename)
                    self.progressbar.setValue(count)
                    count = count + 1
                    QApplication.processEvents()
            QMessageBox.information(
                None,
                "GPM Download ",
                " Download is complete. Please check the download folder",
            )

    # kst 단위 다운로드 방식
    def get_file_list_kst(self, filename):
        kst_list.append(filename)
        donwload_list = []
        dayfile = (
            (filename.split(".")[4]).split("-")[0]
            + "-"
            + (filename.split(".")[4]).split("-")[1]
        )
        filedate = re.search(r"\d{8}", filename).group()
        if filedate + "-S163000" in dayfile:
            num = kst_list.index(filename)
            for ii in range(num - 3):
                kst_list.pop(0)

        if len(kst_list) > 48:
            del kst_list[0:48]

        if len(kst_list) == 48:
            for count in kst_list:
                donwload_list.append(count)
        return donwload_list

    def get_file_list(self):
        if self.gpm_type == "imerg/late" or self.gpm_type == "imerg/early":
            server = "{0}/{1}/{2}/*{3}*".format(
                self.url,
                self.gpm_type,
                self.year + self.month,
                self.year + self.month + self.day,
            )

        if self.gpm_type == "imerg/gis" or self.gpm_type == "imerg/gis/early":
            server = "{0}/{1}/{2}/*{3}*".format(
                self.url,
                self.gpm_type,
                self.year + "/" + self.month,
                self.year + self.month + self.day,
            )

        cmd = "{0} --user={1} --password={1} -qO- {2}".format(
            wget_path, self.userInfo, server
        )
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )

        stdout = process.communicate()[0].decode()
        if stdout[0] == "<":
            print(stdout[0])
            print("No imerg files for the given date")
            return []
        file_list = stdout.split()
        return file_list

    def get_file(self, filenames):
        if self.gpm_type == "imerg/late":
            ftype = "GPM/HDF5/late"
        elif self.gpm_type == "imerg/gis":
            ftype = "GPM/TIFF/late"

        if self.gpm_type == "imerg/early":
            ftype = "GPM/HDF5/early"
        elif self.gpm_type == "imerg/gis/early":
            ftype = "GPM/TIFF/early"

        cmd = "{0} -r -nd -P {1} --limit-rate=20000k --user={2} --password={3} --content-on-error {4}".format(
            wget_path,
            self.donwload_folder + "/" + ftype,
            self.userInfo,
            self.userpass,
            self.url + filenames,
        )
        subprocess.call(cmd, shell=True)
