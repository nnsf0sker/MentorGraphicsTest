import os
import re

pat1 = re.compile(r'Memory Working Set Current\s+=\s+([0-9]*\.[0-9]+|[0-9]+)\s+Mb, Memory Working Set Peak\s+=\s+([0-9]*\.[0-9]+|[0-9]+)\s+Mb')
pat2 = re.compile(r'MESH::Bricks: Total=([0-9]+)\s+Gas=([0-9]+)\s+Solid=([0-9]+)\s+Partial=([0-9]+)\s+Irregular=([0-9]+)')

def MFSP(src):
    res = pat1.findall(src)
    if res and len(res[0]) == 2:
        return float(res[0][1])
    else:
        return -1

def MESH(src):
    res = pat2.findall(src)
    if res and len(res[0]) == 5:
        return int(res[0][0])
    else:
        return -1

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def regularOuput(outputText_,  *files):
    print(outputText_, end="")
    for file in files:
        file.write(outputText_)

def dirSetFilling(folderPath_):
    result = set()
    for k in os.walk(folderPath_):
        for l in range(len(k[2])):
            if k[2][l].endswith(".stdout") == True:
                result.add(os.path.relpath(os.path.join(k[0], k[2][l]), folderPath_))
    return result

def goodViewPath(path):
    return path.replace(os.sep, '/')

def folderExsistCheck (absFolderPath_, *dirs):
    for chekingFolder in dirs:
        if os.path.exists(os.path.join(absFolderPath_, chekingFolder)) != True:
            reportFile = open(os.path.join(absFolderPath_, "report.txt"), 'tw')
            reportFile.write("directory missing: " + str(chekingFolder) + "\n")
            reportFile.close()
            return -1
    return 0

def folderMatching (testFolderPath):
    ft_runFolderPath = os.path.join(testFolderPath, "ft_run")  # Абсолютный путь до папки ft_run текущего теста
    ft_referenceFolderPath = os.path.join(testFolderPath, "ft_reference")  # Абсолютный путь до папки ft_reference текущего теста
    ft_runDirs = list(dirSetFilling(ft_runFolderPath))  # Множество, содержащее подпапки ft_run
    ft_referenceDirs = list(dirSetFilling(ft_referenceFolderPath))  # Множество, содержащее подпапки ft_reference

    if ft_runDirs != ft_referenceDirs:
        reportFile = open(os.path.join(testFolderPath, "report.txt"), 'tw')
        outputText = ""
        step = 0
        for buff in [ft_runDirs, ft_referenceDirs]:
            if len(buff) != 0:
                if step == 0:
                    outputText = outputText + "In ft_run there are extra files files not present in ft_reference: "
                elif step == 1:
                    outputText = outputText + "In ft_run there are missing files present in ft_reference: "
                for m in range(len(buff)):
                    outputText = outputText + "'" + goodViewPath(buff[m]) + "'"
                    if m == (len(buff) - 1):
                        outputText = outputText + "\n"
                    else:
                        outputText = outputText + " "
            step = step + 1
        reportFile.write(outputText)
        reportFile.close()
        return -1
    return ft_runDirs

def ft_FileCheck (filePath_, type ):
    if type == 'ft_run':
        isFlag = 0
    nLine = 1
    runMaxim = -1
    runMESH = -1
    ft_File = open(filePath_, 'tr')
    for line in ft_File:
        if type == 'ft_run':
            if "ERROR" in line.upper():
                ft_File.close()
                return -3, filePath_, nLine, line,
            if line.startswith("Solver finished at"):
                isFlag = 1
            nLine = nLine + 1
        tmp1 = MFSP(line)
        if tmp1 > runMaxim:
            runMaxim = tmp1
            continue
        tmp2 = MESH(line)
        if tmp2 > 0:
            runMESH = tmp2

    ft_File.close()
    if type == 'ft_run':
        if isFlag == 0:
            return -4, filePath_, nLine, line
    return runMaxim, runMESH

def crossFileCheck(folderPath_, listOfDirs):
    errorFlag = 0
    reportFile = open(os.path.join(folderPath_, "report.txt"), 'wt')
    for k in range(len(listOfDirs)):
        tmp1 = ft_FileCheck(os.path.join(folderPath_, "ft_run", listOfDirs[k]), 'ft_run')
        if tmp1[0] == -3:
            errorFlag = 1
            outputText = goodViewPath(os.path.relpath(tmp1[1], os.path.join(folderPath_, 'ft_run') + os.sep) + "(" + str(tmp1[2]) + "): " + tmp1[3])
            reportFile.write(outputText)
            continue
        if tmp1[0] == -4:
            errorFlag = 1
            outputText = goodViewPath(os.path.relpath(tmp1[1], os.path.join(folderPath_, 'ft_run') + os.sep) + ": missing 'Solver finished at'\n")
            reportFile.write(outputText)
            continue
        tmp2 = ft_FileCheck(os.path.join(folderPath_, "ft_reference", listOfDirs[k]), 'ft_reference')
        dif1 = max(tmp1[0], tmp2[0]) / min(tmp1[0], tmp2[0])
        if dif1 > 4:
            errorFlag = 1
            outputText = goodViewPath(listOfDirs[k]) + ": different 'Memory Working Set Peak' (ft_run=" + str(tmp1[0]) + ", ft_reference=" + str(tmp2[0]) + ", rel.diff=" + str(round(dif1, 2) - 1) + ", criterion=4)\n"
            reportFile.write(outputText)
            continue
        dif2 = (max(tmp1[1], tmp2[1]) / min(tmp1[1], tmp2[1])) - 1
        if dif2 > 0.1:
            errorFlag = 1
            outputText = goodViewPath(listOfDirs[k]) + ": different 'Total' of bricks (ft_run=" + str(
                tmp1[1]) + ", ft_reference=" + str(tmp2[1]) + ", rel.diff=" + str(
                toFixed(dif2, 2)) + ", criterion=0.1)\n"
            reportFile.write(outputText)
            continue
    reportFile.close()
    return errorFlag

def oneTestCheck(folderPath_):
    tmp1 = folderExsistCheck(folderPath_, 'ft_run', 'ft_reference')
    if tmp1 == -1:
        return -1
    tmp2 = folderMatching(folderPath_)
    if tmp2 == -1:
        return -1
    tmp3 = crossFileCheck(folderPath_, tmp2)
    if tmp3 == 0:
        return 0
    else:
        return -1

logFolderPath = os.path.join(os.getcwd(), 'logs')  # Абсолютный путь к папке log

f = open('reference_result.txt', 'tw')  # Файл, куда будем писать результаты тестов

for i in sorted(os.listdir(path=logFolderPath)):  # Основной цикл, пробегающий по всем подпапкам всех папок log
    firstSubfoldPath = os.path.join(logFolderPath, i)  # Абсолютный путь до 1-й подпапки
    for j in sorted(os.listdir(path=firstSubfoldPath)):
        secondSubfoldPath = os.path.join(firstSubfoldPath, j)  # Абсолютный путь до 2-й (текущей) папки
        relCurrentFolderPath = os.path.join(i, j)  # Относительный путь папки текущего теста (для вывода)

        result = oneTestCheck(secondSubfoldPath)
        if result == 0:
            outputText = "OK: " + goodViewPath(relCurrentFolderPath + os.sep) + "\n"
            regularOuput(outputText, f)
        elif result == -1:
            with open(os.path.join(secondSubfoldPath, "report.txt"), 'rt') as currentOutputFile:
                outputText = "FAIL: " + goodViewPath(relCurrentFolderPath + os.sep) + "\n" + currentOutputFile.read()
                regularOuput(outputText, f)
f.close()
