import os
import re

def MFSP(input_string):
    tmpString = re.findall(r'Memory Working Set Current = [\d\.]+ Mb, Memory Working Set Peak = [\d\.]+ Mb', input_string)
    if len(tmpString) != 1:
        return -1
    tmpString = re.findall(r'[\d\.]+', input_string)
    try:
        return float(tmpString[1])
    except NaN:
        return -1

def MESH(input_string):
    tmpString = re.findall(r'MESH::Bricks: Total=[\d\.]+ Gas=[\d\.]+ Solid=[\d\.]+ Partial=[\d\.]+ Irregular=[\d\.]+\n', input_string)
    if len(tmpString) != 1:
        return -1
    tmpString = re.findall(r'[\d\.]+', input_string)
    try:
        return int(tmpString[0])
    except NaN:
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
        for buff_ in [list(ft_referenceDirs - ft_runDirs), list(ft_runDirs - ft_referenceDirs)]:
            outputText = "FAIL: " + goodViewPath(relCurrentFolderPath_+os.sep) + "\n"
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
            regularOuput(outputText, mainOutputFile_, localOutputFile_)
            step = step + 1
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

    elif type == 7:  # "0" соостветствует случаю, когда тесты прошли успешно
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

def ft_runFileCheck (filePath_, *parameters_):
    fileName = parameters_[0]
    ft_runFile = open(filePath_, 'tr')
    nLine = 1
    isFlag = 0
    runMaxim = -1
    runMESH = -1
    for line in ft_runFile:
        if "ERROR" in line.upper():
            LogOutput(*tmpList, 3, fileName, nLine, line)
            return -1, -1
        if MFSP(line) > runMaxim:
            runMaxim = MFSP(line)
        if MESH(line) > 0:
            runMESH = MESH(line)
        if line.startswith("Solver finished at"):
            isFlag = 1
        nLine = nLine + 1
    ft_runFile.close()
    if isFlag == 0:
        LogOutput(*tmpList, 4, fileName)
        return -1, -1
    else:
        return runMaxim, runMESH

def ft_referenceFileCheck(filePath_):
    refMaxim = -1
    refMESH = -1
    ft_referenceFile = open(filePath_, 'tr')
    for line in ft_referenceFile:
        if MFSP(line) > refMaxim:
            refMaxim = MFSP(line)
        if MESH(line) > 0:
            refMESH = MESH(line)
    ft_referenceFile.close()
    return refMaxim, refMESH

def crossFileCheck(folderPath_, setOfDirs, *tmpList):
    for k in range(len(setOfDirs)):
        runTemp = ft_runFileCheck(os.path.join(folderPath_, "ft_run", setOfDirs[k]), setOfDirs[k])
        if runTemp[0] == -1:
            continue
        refTemp = ft_referenceFileCheck(os.path.join(folderPath_, "ft_reference", setOfDirs[k]))
        if refTemp[0] == -1:
            continue
        if max(runTemp[0], refTemp[0]) / min(runTemp[0], refTemp[0]) > 4:
            LogOutput(*tmpList, 5, buffSet[k], runTemp[0], refTemp[0])
        if (max(runTemp[1], refTemp[1]) / min(runTemp[1], refTemp[1]) - 1) > 0.1:
            LogOutput(*tmpList, 6, buffSet[k], runTemp[1], refTemp[1])

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

        if folderExsistCheck(secondSubfoldPath, *tmpList) != 1:
            continue

        flag, buffSet = folderMatching(secondSubfoldPath, *tmpList)
        if flag != 1:
            continue

        crossFileCheck(secondSubfoldPath, buffSet, *tmpList)

        LogOutput(*tmpList, 7)  # Запустится только, если вывода ещё не было

f.close()
