import os

directrory = os.getcwd()

f = open('reference_result_1.txt', 'tw')

a = "12.345"
print(float(a[0:1])+1)

def MFSP (input_string):
    if input_string.startswith("Memory Working Set Current = "):
        Mb1_index = input_string.index(' Mb')
        Mb2_index = input_string.index(' Mb', Mb1_index+1)
        first_num = float(input_string[29:Mb1_index])
        second_num = float(input_string[Mb1_index+31:Mb2_index])
        return first_num, second_num
    else:
        return -1, -1

def MESH (input_string):
    if input_string.startswith("MESH::Bricks: Total="):
        Mb1_index = input_string.index('Gas')
        return (int(input_string[20:Mb1_index-1]))
    else:
        return -1;

for i in os.listdir(path=directrory + "/" + "logs"):
    for j in os.listdir(path=directrory + "/" + "logs" + "/" + i):
        hasOutput = 0
        if (os.path.exists(directrory + "/" + "logs" + "/" + i + "/" + j + "/" + "ft_reference") != True):
            hasOutput = 1
            f.write("FAIL: "+i+"/"+j+"\n")
            f.write("directory missing: ft_reference\n")
            # Записываем в файл отсутствие папки ft_reference
            continue
        if (os.path.exists(directrory + "/" + "logs" + "/" + i + "/" + j + "/" + "ft_run") != True):
            hasOutput = 1
            f.write("FAIL: "+i+"/"+j+"\n")
            f.write("directory missing: ft_reference\n")
            # Записываем в файл отсутствие папки ft_run
            continue

        rel_path = directrory + "/" + "logs" + "/" + i + "/" + j + "/"
        run_path = rel_path + "ft_run"
        ref_path = rel_path + "ft_reference"

        ListOfDirsRun = os.listdir(path=run_path)
        ListOfDirsReference = os.listdir(path=ref_path)

        ft_runBuff = []
        ft_referenceBuff = []
        set_ft_runBuff = set()
        set_ft_referenceBuff = set()

        for k in os.walk(rel_path + "ft_run"):
            for l in range(len(k[2])):
                if (k[2][l].endswith(".stdout") == True):
                    set_ft_runBuff.add(os.path.relpath(k[0], run_path)+"/"+k[2][l])

        for k in os.walk(rel_path + "ft_reference"):
            for l in range(len(k[2])):
                if (k[2][l].endswith(".stdout") == True):
                    set_ft_referenceBuff.add(os.path.relpath(k[0], ref_path)+"/"+k[2][l])

        if (set_ft_runBuff != set_ft_referenceBuff):
            hasOutput = 1
            f.write("FAIL: "+i+"/"+j+"\n")

            setr = list(set_ft_referenceBuff - set_ft_runBuff)
            if(len(setr)!=0):
                f.write("In ft_run there are missing files present in ft_reference: ")
                for m in range(len(setr)):
                    f.write("'"+setr[m]+"'")
                    if m == (len(setr)-1):
                        f.write("\n")
                    else:
                        f.write(" ")

            setr = list(set_ft_runBuff - set_ft_referenceBuff)
            if (len(setr) != 0):
                f.write("In ft_run there are extra files files not present in ft_reference: ")
                for m in range(len(setr)):
                    f.write("'" + setr[m] + "'")
                    if m == (len(setr)-1):
                        f.write("\n")
                    else:
                        f.write(" ")

            continue

        setr = list(set_ft_runBuff)
        for k in range(len(setr)):
            run_file = open(run_path+"/"+setr[k], 'tr')
            nLine = 1
            isError = 0
            isFlag = 0

            for line in run_file:
                if "ERROR" in line.upper():
                    hasOutput = 1
                    f.write("FAIL: " + i + "/" + j + "\n")
                    f.write(setr[k]+"("+str(nLine)+") "+ line)
                    isError = 1
                    break

                if line.startswith("Solver finished at"):
                    isFlag = 1

            if (isError==0)&(isFlag==0):
                hasOutput = 1
                f.write("FAIL: " + i + "/" + j + "\n")
                f.write(setr[k]+": missing 'Solver finished at'\n")

            run_file.close()

            if (isError==0)&(isFlag==1):
                run_file = open(run_path + "/" + setr[k], 'tr')
                ref_file = open(ref_path+"/"+setr[k], 'tr')

                runMaxim = -1
                refMaxim = -1
                runMESH = -1
                refMESH = -1
                for line in run_file:
                    if MFSP(line)[1] > runMaxim:
                        runMaxim = MFSP(line)[1]
                    if MESH(line)>0:
                        runMESH = MESH(line)

                for line in ref_file:
                    if MFSP(line)[1] > refMaxim:
                        refMaxim = MFSP(line)[1]
                    if MESH(line)>0:
                        refMESH = MESH(line)

                diffMax = max(runMaxim, refMaxim)/min(runMaxim, refMaxim)
                diffMESH = max(runMESH, refMESH)/min(runMESH, refMESH)
                # print(refMaxim, runMaxim, diff)

                if (diffMax > 4):
                    hasOutput = 1
                    f.write("FAIL: " + i + "/" + j + "\n")
                    f.write(setr[k]+": different 'Memory Working Set Peak' (ft_run="+str(runMaxim)+", ft_reference="+str(refMaxim)+", rel.diff="+str(round(diffMax-1,2))+", criterion=4)\n")

                if ((diffMESH-1) > 0.1):
                    hasOutput = 1
                    f.write("FAIL: " + i + "/" + j + "\n")
                    f.write(setr[k] + ": different 'Total' of bricks (ft_run=" + str(runMESH) + ", ft_reference=" + str(refMESH) + ", rel.diff=" + str(round(diffMESH - 1, 2)) + ", criterion=0.1)\n")
                ref_file.close()

        if hasOutput == 0:
            hasOutput = 1
            f.write("OK: " + i + "/" + j + "\n")
            run_file.close()



f.close()