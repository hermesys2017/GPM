# -*- coding: utf-8 -*-


import sys, os, subprocess, getpass
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QDir
from time import sleep
from osgeo import gdal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Util

_util = Util.util()


sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/Lib")

# gdal을 사용하기 위한 환경 설정
qgis_paths = QgsApplication.showSettings()
qgis_paths = qgis_paths.split("\n")

qgis_path = str(os.path.dirname(os.path.dirname(str(qgis_paths[1].split("\t\t")[1]))))


# osgeo4w="C:/Program Files/QGIS 3.8/OSGeo4W.bat"
osgeo4w = qgis_path + "/OSGeo4W.bat"
# saga_path = "C:/Program Files/QGIS 3.8/apps/saga-ltr/saga_cmd.exe"
saga_path = qgis_path + "/apps/saga-ltr/saga_cmd.exe"  # 3.10때까지는 이 경로였음.
saga_path = (
    qgis_path + "/apps/saga/saga_cmd.exe"
)  # 2023.01.25 조 : 3.22.14 LTR 에서 경로가 변경됨.

# _tempFolderSuffix = unicode(uuid.uuid4()).replace('-', '')


class accum_util:
    def tempFolder(self):
        tempDir = os.path.join(
            unicode(QDir.tempPath()), "processing" + _tempFolderSuffix
        )
        if not QDir(tempDir).exists():
            QDir().mkpath(tempDir)

        return unicode(os.path.abspath(tempDir))

    def saga_gridssum(self, TIFF_list, output):
        # 환경 설정
        #         saga_ltr=os.environ["SAGA"] = 'C:/Program Files/QGIS 3.8/apps/saga-ltr'
        #         saga_modules=os.environ["SAGA_MLB"] ='C:/Program Files/QGIS 3.8/apps/saga-ltr/modules'
        saga_ltr = os.environ["SAGA"] = qgis_path + "/apps/saga-ltr"
        saga_modules = os.environ["SAGA_MLB"] = qgis_path + "/apps/saga-ltr/modules"
        print(saga_modules)
        print(qgis_path)
        #         PATH=os.environ["PATH"]='C:/PROGRA~1/QGIS2~1.18/apps/Python27/lib/site-packages/Shapely-1.2.18-py2.7-win-amd64.egg/shapely/DLLs;C:/PROGRA~1/QGIS2~1.18/apps/Python27/DLLs;C:/PROGRA~1/QGIS2~1.18/apps/Python27/lib/site-packages/numpy/core;C:/PROGRA~1/QGIS2~1.18/apps/qgis-ltr/bin;C:/PROGRA~1/QGIS2~1.18/apps/Python27/Scripts;C:/PROGRA~1/QGIS2~1.18/bin;C:/WINDOWS/system32;C:/WINDOWS;C:/WINDOWS/system32/WBem;C:/PROGRA~1/QGIS2~1.18/apps/saga-ltr;C:/PROGRA~1/QGIS2~1.18/apps/saga-ltr/modules'

        onelist = []
        for file in TIFF_list:
            filename = _util.GetFilename(file)
            onelist.append(file)
            listTostr = ";".join(onelist)

            list = []
            try:
                grids = " -GRIDS {}".format(listTostr)
                results = " -RESULT {}".format(output)
                #                 run_saga=saga_path+" grid_calculus 8 {0} {1}".format(grids,results)
                run_saga = [
                    osgeo4w,
                    saga_path,
                    "grid_calculus",
                    "8",
                    "-GRIDS",
                    listTostr,
                    #                           "-USE_NODATA","true",
                    "-RESULT",
                    output,
                ]

                #                 arg="gdal_calc -A {0} --format GTiff --calc A --outfile={1} ").format(str(list[0]),outputfile)

                print(run_saga)
                # nodata 추가함
                #                 create_file.write(str(run_saga)+"\n")
                #                 call_arg =[osgeo4w,run_saga]
                #                 os.system(run_saga)
                subprocess.call(run_saga, shell=True)
                #                 subprocess.call(run_saga)
                sleep(0.1)

                #                 subprocess.call(run_saga, shell=True) #나중에 shell=True 사용해서 cmd 안뜨게 함/

                input_path = os.path.dirname(output)
                for dirfile in os.listdir(input_path):
                    if dirfile.endswith(".sdat"):
                        self.gdal_format_convert(input_path + "/" + dirfile, output)
                self.saga_file_remove(output)

            except Exception as e:
                _util.MessageboxShowError("Accum", str(e))

    #         create_file.close()
    def gdal_format_convert(self, input, output):
        #         arg = "gdal_translate -of GTiff "
        #         arg = arg +" " + input+" " + output
        call_arg = [osgeo4w, "gdal_translate", "-of", "GTiff", input, output]

        subprocess.call(call_arg, shell=True)

    #         create_file.write(arg)
    #         os.system(arg)

    def saga_file_remove(self, input):
        input_path = os.path.dirname(input)
        # tif 외 파일 전부 삭제
        for dirfile in os.listdir(input_path):
            if os.path.splitext(dirfile)[1] in [
                ".sdat",
                ".sgrd",
                ".mgrd",
                ".prj",
                ".xml",
            ]:
                os.remove(input_path + "/" + dirfile)

    # =========== Accum Amount 값 ===========
    def accum_amount(self, input, output):
        tiff_ds = gdal.Open(input)
        Nodata = tiff_ds.GetRasterBand(1).GetNoDataValue()
        username = getpass.getuser()
        #         gdal_calc ="C:/Users/\"{0}\"/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/Kict_Satellite_Precipitation_Converter/Lib/gdal/gdal_calc.py".format(format(username))
        if Nodata != None:
            call_arg = [
                osgeo4w,
                #                         "python",
                "gdal_calc",
                "-A",
                input,
                "--format",
                "GTiff",
                "--calc",
                "A*30/60",
                "--outfile",
                str(output),
                "--NoDataValue",
                str(Nodata),
            ]

        #             call_arg = 'gdal_calc -A "{0}" --format GTiff --calc A*30/60 --outfile "{1}" --NoDataValue {2}'.format(input,output,Nodata)

        if Nodata == None:
            call_arg = [
                osgeo4w,
                #                         "python",
                gdal_calc,
                "-A",
                input,
                "--format",
                "GTiff",
                "--calc",
                "A*30/60",
                "--outfile",
                str(output),
                "--NoDataValue",
                "-9999",
            ]
        #             call_arg = 'gdal_calc -A "{0}" --format GTiff --calc A*30/60 --outfile "{1}" --NoDataValue -9999'.format(input,output)
        #         call_arg = "{0} -A {1} --format GTiff --calc A*30/60 --outfile {2} --NoDataValue -9999".format(gdal_calc,input,output)
        #             call_arg = "gdal_calc -A {0} --format GTiff --calc A*30/60 --outfile {1} --NoDataValue -9999".format(input,output)

        print(call_arg)

        subprocess.call(call_arg, shell=True)
        #         os.system(call_arg)
        sleep(0.2)

    # ====== Amount 파일 삭제
    def amount_remove(self, output):
        #         Fpath= os.path.dirname(output)
        #         for dir in os.listdir(Fpath):
        #             if "_Amount.tif" in dir:
        #                 os.remove(Fpath+"/"+dir)
        os.remove(output)

    # ========= Accum 시간 별 계산 ===========
    def Accum_hour(self, list, outputfile):
        # ======1H  =======
        #         if check == "1H":
        self.saga_gridssum(list, outputfile)

    # =================처음 시도한 ACCUM GRID SUM CALC=====================
    def accum_band(self, list, outputfile):
        if len(list) == 1:
            arg = gdal_calc + (" -A {0} --format GTiff --calc A --outfile={1} ").format(
                str(list[0]), outputfile
            )
            call_value = os.system(arg)
            return call_value

        if len(list) == 2:
            arg = gdal_calc + (
                " -A {0} -B {1} --format GTiff --calc A+B --outfile={2}   "
            ).format(str(list[0]), str(list[1]), outputfile)
            run = os.system(arg)
            return run

        if len(list) == 3:
            arg = gdal_calc + (
                " -A {0} -B {1} -C {2} --format GTiff --calc A+B+C --outfile={3}   "
            ).format(str(list[0]), str(list[1]), str(list[2]), outputfile)
            run = os.system(arg)
            return run

        if len(list) == 4:
            arg = gdal_calc + (" -A {0} -B {1} -C {2} -D {3} ").format(
                str(list[0]), str(list[1]), str(list[2]), str(list[3])
            )
            arg = arg + (" --format GTiff  --calc A+B+C+D --outfile={0}  ").format(
                outputfile
            )
            run = os.system(arg)
            return run

        if len(list) == 5:
            arg = gdal_calc + (
                " -A {0} -B {1} -C {2} -D {3} -E {4} --format GTiff --calc A+B+C+D+E --outfile={5}  "
            ).format(
                str(list[0]),
                str(list[1]),
                str(list[2]),
                str(list[3]),
                str(list[4]),
                outputfile,
            )
            run = os.system(arg)
            return run

        if len(list) == 6:
            arg = gdal_calc + (
                " -A {0} -B {1} -C {2} -D {3} -E {4} -F {5} --format GTiff --calc A+B+C+D+E+F --outfile={6}  "
            ).format(
                str(list[0]),
                str(list[1]),
                str(list[2]),
                str(list[3]),
                str(list[4]),
                str(list[5]),
                outputfile,
            )
            run = os.system(arg)
            return run

        if len(list) == 7:
            arg = gdal_calc + (
                " -A {0} -B {1} -C {2} -D {3} -E {4} -F {5} -G {6} --format GTiff --calc A+B+C+D+E+F+G --outfile={7}  "
            ).format(
                str(list[0]),
                str(list[1]),
                str(list[2]),
                str(list[3]),
                str(list[4]),
                str(list[5]),
                str(list[6]),
                outputfile,
            )
            run = os.system(arg)
            return run

        if len(list) == 8:
            arg = gdal_calc + (
                " -A {0} -B {1} -C {2} -D {3} -E {4} -F {5} -G {6} -H {7}"
            ).format(
                str(list[0]),
                str(list[1]),
                str(list[2]),
                str(list[3]),
                str(list[4]),
                str(list[5]),
                str(list[6]),
                str(list[7]),
            )
            arg = arg + (
                " --format GTiff --calc A+B+C+D+E+F+G+H --outfile={0}   "
            ).format(outputfile)
            run = os.system(arg)
            return run

        if len(list) == 9:
            arg = gdal_calc + (
                " -A {0} -B {1} -C {2} -D {3} -E {4} -F {5} -G {6} -H {7} -I {8}"
            ).format(
                str(list[0]),
                str(list[1]),
                str(list[2]),
                str(list[3]),
                str(list[4]),
                str(list[5]),
                str(list[6]),
                str(list[7]),
                str(list[8]),
            )
            arg = arg + (
                " --format GTiff --calc A+B+C+D+E+F+G+H+I --outfile={0}   "
            ).format(outputfile)
            run = os.system(arg)
            return run

        if len(list) == 10:
            arg = gdal_calc + (
                " -A {0} -B {1} -C {2} -D {3} -E {4} -F {5} -G {6} -H {7} -I {8} -J {9}"
            ).format(
                str(list[0]),
                str(list[1]),
                str(list[2]),
                str(list[3]),
                str(list[4]),
                str(list[5]),
                str(list[6]),
                str(list[7]),
                str(list[8]),
                str(list[9]),
            )
            arg = arg + (
                " --format GTiff --calc A+B+C+D+E+F+G+H+I+J --outfile={0}   "
            ).format(outputfile)
            run = os.system(arg)
            return run
