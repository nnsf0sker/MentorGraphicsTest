import os

def MFSP(input_string):
    if input_string.startswith("Memory Working Set Current = "):
        return float(input_string[(input_string.index(' Mb') + 31):-3])
    else:
        return -1


def MESH(input_string):
    if input_string.startswith("MESH::Bricks: Total="):
        return (int(input_string[20:(input_string.index('Gas') - 1)]))
    else:
        return -1;

manyOutputError = 0

directrory = os.getcwd()  # Абсолютный путь к папке, где находится программа

logFolderPath = os.path.join(directrory, "logs")  # Абсолютный путь к папке log

f = open('reference_result.txt', 'tw')  # Файл, куда будем писать результаты тестов

for i in os.listdir(path=logFolderPath):  # Основной цикл, пробегающий по всем подпапкам всех папок log
    firstSubfoldPath = os.path.join(logFolderPath, i)
    for j in os.listdir(path=firstSubfoldPath):
        secondSubfoldPath = os.path.join(firstSubfoldPath, j)  # Абсолютный путь к текущей папке
        relCurrentFolderPath = os.path.join(i, j)  # Относительный путь папки текущего теста (для вывода)
        hasOutput = 0  # Флаг, был ли вывод для данного теста
        currentOutputFile = open(os.path.join(secondSubfoldPath, "report.txt"), 'tw')

        if os.path.exists(os.path.join(secondSubfoldPath, "ft_reference")) != True:
            # hasOutput = 1
            f.write("FAIL: " + relCurrentFolderPath + "/\n")
            f.write("directory missing: ft_reference\n")
            currentOutputFile.write("FAIL: " + relCurrentFolderPath + "/\n")
            currentOutputFile.write("directory missing: ft_reference\n")
            currentOutputFile.close()
            # Записываем в файл отсутствие папки ft_reference
            continue

        if os.path.exists(os.path.join(secondSubfoldPath, "ft_run")) != True:
            # hasOutput = 1
            f.write("FAIL: " + relCurrentFolderPath + "/\n")
            f.write("directory missing: ft_run\n")
            currentOutputFile.write("FAIL: " + relCurrentFolderPath + "/\n")
            currentOutputFile.write("directory missing: ft_run\n")
            currentOutputFile()
            # Записываем в файл отсутсвие папки ft_run
            continue

        ft_runFolderPath = os.path.join(secondSubfoldPath, "ft_run")  # Абсолютный путь до папки ft_run текущего теста
        ft_referenceFolderPath = os.path.join(secondSubfoldPath, "ft_reference")  # Абсолютный путь до папки ft_reference текущего теста

        ft_runDirs = set()  # Множество, содержащее подпапки ft_run
        ft_referenceDirs = set()  # Множество, содержащее подпапки ft_reference

        for k in os.walk(ft_runFolderPath):
            for l in range(len(k[2])):
                if (k[2][l].endswith(".stdout") == True):
                    ft_runDirs.add(os.path.relpath(os.path.join(k[0], k[2][l]), ft_runFolderPath))

        for k in os.walk(ft_referenceFolderPath):
            for l in range(len(k[2])):
                if (k[2][l].endswith(".stdout") == True):
                    ft_referenceDirs.add(os.path.relpath(os.path.join(k[0], k[2][l]), ft_referenceFolderPath))

        if ft_runDirs != ft_referenceDirs:  # Вывод в случае, если *.stdout файлы в ft_run и ft_reference не совпадают
            hasOutput = 1
            f.write("FAIL: " + relCurrentFolderPath + "/\n")
            currentOutputFile.write("FAIL: " + relCurrentFolderPath + "/\n")

            buffSet = list(ft_referenceDirs - ft_runDirs)
            if (len(buffSet) != 0):
                f.write("In ft_run there are missing files present in ft_reference: ")
                currentOutputFile.write("In ft_run there are missing files present in ft_reference: ")

                for m in range(len(buffSet)):
                    f.write("'" + buffSet[m] + "'")
                    currentOutputFile.write("'" + buffSet[m] + "'")
                    if m == (len(buffSet) - 1):
                        f.write("\n")
                        currentOutputFile.write("\n")
                    else:
                        f.write(" ")
                        currentOutputFile.write(" ")

            buffSet = list(ft_runDirs - ft_referenceDirs)
            if (len(buffSet) != 0):
                f.write("In ft_run there are extra files files not present in ft_reference: ")
                currentOutputFile.write("In ft_run there are extra files files not present in ft_reference: ")
                for m in range(len(buffSet)):
                    f.write("'" + buffSet[m] + "'")
                    currentOutputFile.write("'" + buffSet[m] + "'")
                    if m == (len(buffSet) - 1):
                        f.write("\n")
                        currentOutputFile.write("\n")
                    else:
                        f.write(" ")
                        currentOutputFile.write(" ")

            currentOutputFile.close()
            continue

        buffSet = list(ft_runDirs)
        for k in range(len(buffSet)):
            ft_runFile = open(os.path.join(ft_runFolderPath, buffSet[k]), 'tr')
            nLine = 1
            isError = 0
            isFlag = 0

            for line in ft_runFile:
                if "ERROR" in line.upper():
                    if hasOutput == 0:
                        hasOutput = 1
                        f.write("FAIL: " + relCurrentFolderPath + "/\n")
                        f.write(buffSet[k] + "(" + str(nLine) + ") " + line)
                        currentOutputFile.write("FAIL: " + relCurrentFolderPath + "/\n")
                        currentOutputFile.write(buffSet[k] + "(" + str(nLine) + ") " + line)
                        currentOutputFile.close()
                        isError = 1
                        break
                    else:
                        manyOutputError = 1
                        #print("ERROR!!!")

                if line.startswith("Solver finished at"):
                    isFlag = 1
                nLine = nLine + 1

            if (isError == 0) & (isFlag == 0):
                if hasOutput == 0:
                    hasOutput = 1
                    f.write("FAIL: " + relCurrentFolderPath + "/\n")
                    f.write(buffSet[k] + ": missing 'Solver finished at'\n")
                    currentOutputFile.write("FAIL: " + relCurrentFolderPath + "/\n")
                    currentOutputFile.write(buffSet[k] + ": missing 'Solver finished at'\n")
                    currentOutputFile.close()
                else:
                    manyOutputError = 1
                    #print("ERROR!!!")

            ft_runFile.close()

            if (isError == 0) & (isFlag == 1):
                ft_runFile = open(os.path.join(ft_runFolderPath, buffSet[k]), 'tr')
                ft_referenceFile = open(os.path.join(ft_referenceFolderPath, buffSet[k]), 'tr')

                runMaxim = -1
                refMaxim = -1
                runMESH = -1
                refMESH = -1
                for line in ft_runFile:
                    if MFSP(line) > runMaxim:
                        runMaxim = MFSP(line)
                    if MESH(line) > 0:
                        runMESH = MESH(line)

                for line in ft_referenceFile:
                    if MFSP(line) > refMaxim:
                        refMaxim = MFSP(line)
                    if MESH(line) > 0:
                        refMESH = MESH(line)

                diffMax = max(runMaxim, refMaxim) / min(runMaxim, refMaxim)
                diffMESH = max(runMESH, refMESH) / min(runMESH, refMESH)

                if diffMax > 4:
                    if hasOutput == 0:
                        hasOutput = 1
                        f.write("FAIL: " + relCurrentFolderPath + "/\n")
                        f.write(buffSet[k] + ": different 'Memory Working Set Peak' (ft_run=" + str(
                            runMaxim) + ", ft_reference=" + str(refMaxim) + ", rel.diff=" + str(
                            round(diffMax - 1, 2)) + ", criterion=4)\n")
                        currentOutputFile.write("FAIL: " + relCurrentFolderPath + "/\n")
                        currentOutputFile.write(buffSet[k] + ": different 'Memory Working Set Peak' (ft_run=" + str(
                            runMaxim) + ", ft_reference=" + str(refMaxim) + ", rel.diff=" + str(
                            round(diffMax - 1, 2)) + ", criterion=4)\n")
                        currentOutputFile.close()
                    else:
                        manyOutputError = 1
                        #print("ERROR!!!")

                if (diffMESH - 1) > 0.1:
                    if hasOutput == 0:
                        hasOutput = 1
                        f.write("FAIL: " + relCurrentFolderPath + "/\n")
                        f.write(buffSet[k] + ": different 'Total' of bricks (ft_run=" + str(runMESH) + ", ft_reference=" + str(
                            refMESH) + ", rel.diff=" + str(round(diffMESH - 1, 2)) + ", criterion=0.1)\n")
                        currentOutputFile.write("FAIL: " + relCurrentFolderPath + "/\n")
                        currentOutputFile.write(
                            buffSet[k] + ": different 'Total' of bricks (ft_run=" + str(runMESH) + ", ft_reference=" + str(
                                refMESH) + ", rel.diff=" + str(round(diffMESH - 1, 2)) + ", criterion=0.1)\n")
                        currentOutputFile.close()
                    else:
                        manyOutputError = 1
                        #print("ERROR!!!")

                ft_referenceFile.close()
                ft_runFile.close()

        if hasOutput == 0:
            hasOutput = 1
            f.write("OK: " + relCurrentFolderPath + "/\n")
            currentOutputFile.write("OK: " + relCurrentFolderPath + "/\n")
            currentOutputFile.close()

f.close()
