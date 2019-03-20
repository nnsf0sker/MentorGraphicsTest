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
        return float(res[0][0])
    else:
        return -1

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def regularOuput(outputText_,  *files):
    print(outputText_, end="")
    for file in files:
        file.write(outputText_)

def LogOutput(mainOutputFile_, localOutputFile_, relCurrentFolderPath_, type, *parameters_):
    global hasOutput
    if hasOutput == 1:
        return
    hasOutput = 1

    if type == 1:  # "1" соостветствует случаю, когда отсутствует папка ft_reference или ft_run
        outputText = "FAIL: " + goodViewPath(relCurrentFolderPath_+os.sep) + "\n" + "directory missing: " + parameters_[0] + "\n" # parameters_[0] - это название отсутствующей папки
        regularOuput(outputText, mainOutputFile_, localOutputFile_)
        localOutputFile_.close()

    elif type == 2:  # "2" соостветствует случаю, когда *.stdout файлы в папках ft_reference и ft_run не совпадают
        ft_referenceDirs = parameters_[0]
        ft_runDirs = parameters_[1]
        step = 0
        outputText = "FAIL: " + goodViewPath(relCurrentFolderPath_+os.sep) + "\n"
        for buff_ in [list(ft_referenceDirs - ft_runDirs), list(ft_runDirs - ft_referenceDirs)]:
            if (len(buff_) != 0):
                if step == 0:
                    outputText = outputText + "In ft_run there are missing files present in ft_reference: "
                elif step == 1:
                    outputText = outputText + "In ft_run there are extra files files not present in ft_reference: "
                for m in range(len(buff_)):
                    outputText = outputText + "'" + goodViewPath(buff_[m]) + "'"
                    if m == (len(buff_) - 1):
                        outputText = outputText + "\n"
                    else:
                        outputText = outputText + " "
            step = step + 1
        regularOuput(outputText, mainOutputFile_, localOutputFile_)
        localOutputFile_.close()

    elif type == 3:  # "3" соответствует выводу, когда в *stdout - файле папки ft_rub есть слово "ERROR"
        buffSetFile_ = parameters_[0]
        nLine_ = parameters_[1]
        line_ = parameters_[2]
        outputText = "FAIL: " + goodViewPath(relCurrentFolderPath_+os.sep) + "\n" + goodViewPath(buffSetFile_) + "(" + str(nLine_) + "): " + line_
        regularOuput(outputText, mainOutputFile_, localOutputFile_)
        localOutputFile_.close()

    elif type == 4:  # "4" соответствует выводу, когда в *stdout - файле папки ft_rub нет строки 'Solver finished at'
        buffSetFile_ = parameters_[0]
        outputText = "FAIL: " + goodViewPath(relCurrentFolderPath_+os.sep) + "\n" + goodViewPath(buffSetFile_) + ": missing 'Solver finished at'\n"
        regularOuput(outputText, mainOutputFile_, localOutputFile_)
        localOutputFile_.close()

    elif type == 5:  # "5" соответствует выводу, когда MFSP различается более чем в 4 раза
        buffSet_ = parameters_[0]
        runMaxim = parameters_[1]
        refMaxim = parameters_[2]
        diffMax = max(runMaxim, refMaxim) / min(runMaxim, refMaxim)
        outputText = "FAIL: " + goodViewPath(relCurrentFolderPath_+os.sep) + "\n" + goodViewPath(buffSet_) + ": different 'Memory Working Set Peak' (ft_run=" + str(
            runMaxim) + ", ft_reference=" + str(refMaxim) + ", rel.diff=" + str(
            round(diffMax - 1, 2)) + ", criterion=4)\n"
        regularOuput(outputText, mainOutputFile_, localOutputFile_)
        localOutputFile_.close()

    elif type == 6:  #
        buffSet_ = parameters_[0]
        runMESH = parameters_[1]
        refMESH = parameters_[2]
        diffMESH = max(runMESH, refMESH) / min(runMESH, refMESH)
        outputText = "FAIL: " + goodViewPath(relCurrentFolderPath_+os.sep) + "\n" + goodViewPath(buffSet_) + ": different 'Total' of bricks (ft_run=" + str(runMESH) + ", ft_reference=" + str(
                refMESH) + ", rel.diff=" + str(toFixed(diffMESH - 1, 2)) + ", criterion=0.1)\n"
        regularOuput(outputText, mainOutputFile_, localOutputFile_)
        localOutputFile_.close()

    elif type == 7:  # "7" соостветствует случаю, когда тесты прошли успешно
        outputText = "OK: " + goodViewPath(relCurrentFolderPath_+os.sep) + "\n"
        regularOuput(outputText, mainOutputFile_)
        localOutputFile_.close()

def dirSetFilling(setName_, folderPath_):
    for k in os.walk(folderPath_):
        for l in range(len(k[2])):
            if k[2][l].endswith(".stdout") == True:
                setName_.add(os.path.relpath(os.path.join(k[0], k[2][l]), folderPath_))

def goodViewPath(path):
    return path.replace(os.sep, '/')

def folderExsistCheck (absFolderPath_, *tmpList):
    for chekingFolder in ["ft_reference", "ft_run"]:
        if os.path.exists(os.path.join(absFolderPath_, chekingFolder)) != True:
            LogOutput(*tmpList, 1, chekingFolder)
            return -1
    return 1

def folderMatching (testFolderPath, *tmpList):
    ft_runFolderPath = os.path.join(testFolderPath, "ft_run")  # Абсолютный путь до папки ft_run текущего теста
    ft_referenceFolderPath = os.path.join(testFolderPath, "ft_reference")  # Абсолютный путь до папки ft_reference текущего теста
    ft_runDirs = set()  # Множество, содержащее подпапки ft_run
    ft_referenceDirs = set()  # Множество, содержащее подпапки ft_reference
    for p in [[ft_runDirs, ft_runFolderPath], [ft_referenceDirs, ft_referenceFolderPath]]:  # Заполнение множеств папок с *.stdout файлами
        dirSetFilling(*p)
    if ft_runDirs != ft_referenceDirs:  # Вывод в случае, если *.stdout файлы в ft_run и ft_reference не совпадают
        LogOutput(*tmpList, 2, ft_referenceDirs, ft_runDirs)
        return -1, list(set())
    return 1, list(ft_runDirs)

def ft_FileCheck (filePath_, type , *parameters_):
    if type == 'ft_run':
        fileName = parameters_[0]
        nLine = 1
        isFlag = 0
    runMaxim = -1
    runMESH = -1
    ft_runFile = open(filePath_, 'tr')
    for line in ft_runFile:
        if type == 'ft_run':
            if "ERROR" in line.upper():
                ft_runFile.close()
                return [-1, nLine, line]
            if line.startswith("Solver finished at"):
                isFlag = 1
            nLine = nLine + 1
        tmp = MFSP(line)
        if tmp > runMaxim:
            runMaxim = tmp
            continue
        tmp = MESH(line)
        if tmp > 0:
            runMESH = tmp

    ft_runFile.close()
    if type == 'ft_run':
        if isFlag == 0:
            return [-2, *tmpList, 4, fileName]
    return runMaxim, runMESH

def crossFileCheck(folderPath_, setOfDirs, *tmpList):
    for k in range(len(setOfDirs)):
        runTemp = ft_FileCheck(os.path.join(folderPath_, "ft_run", setOfDirs[k]), 'ft_run', setOfDirs[k])
        if runTemp[0] == -1:
            LogOutput(*tmpList, 3, setOfDirs[k], runTemp[1], runTemp[2])
            continue
        if runTemp[0] == -2:
            LogOutput(*tmpList, 4, setOfDirs[k])
            continue
        refTemp = ft_FileCheck (os.path.join(folderPath_, "ft_reference", setOfDirs[k]), 'ft_reference')
        if refTemp[0] == -1:
            continue
        if max(runTemp[0], refTemp[0]) / min(runTemp[0], refTemp[0]) > 4:
            LogOutput(*tmpList, 5, setOfDirs[k], runTemp[0], refTemp[0])
        if (max(runTemp[1], refTemp[1]) / min(runTemp[1], refTemp[1])) - 1 > 0.1:
            LogOutput(*tmpList, 6, setOfDirs[k], runTemp[1], refTemp[1])

def oneTestCheck(folderPath_, *tmpList):
    if folderExsistCheck(folderPath_, *tmpList) != 1:
        return -1
    flag, buffSet = folderMatching(folderPath_, *tmpList)
    if flag != 1:
        return -1
    crossFileCheck(folderPath_, buffSet, *tmpList)
    return 1

tmpList = [0, 0, 0]

logFolderPath = os.path.join(os.getcwd(), "logs")  # Абсолютный путь к папке log

f = open('reference_result.txt', 'tw')  # Файл, куда будем писать результаты тестов

tmpList[0] = f

for i in sorted(os.listdir(path=logFolderPath)):  # Основной цикл, пробегающий по всем подпапкам всех папок log
    firstSubfoldPath = os.path.join(logFolderPath, i)  # Абсолютный путь до 1-й подпапки
    for j in sorted(os.listdir(path=firstSubfoldPath)):
        secondSubfoldPath = os.path.join(firstSubfoldPath, j)  # Абсолютный путь до 2-й (текущей) папки
        relCurrentFolderPath = os.path.join(i, j)  # Относительный путь папки текущего теста (для вывода)
        hasOutput = 0  # Флаг, был ли вывод
        currentOutputFile = open(os.path.join(secondSubfoldPath, "report.txt"), 'tw')  # Путь к промежуточному файлу вывода
        tmpList[1] = currentOutputFile
        tmpList[2] = relCurrentFolderPath

        if oneTestCheck(secondSubfoldPath, *tmpList) != 1:
            continue
        LogOutput(*tmpList, 7)  # Запустится только, если вывода ещё не было
f.close()
