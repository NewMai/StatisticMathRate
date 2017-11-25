



# Get one block from file pointer : f 
# Return a tube containing the block's info
def GetOneBlock(f):
    block = list()
    isFirstInst = 1
    addr = ""
    while True:
        line = f.readline()
        if line == "":         # Reached the file end
            break
        if "Trace:" in line:   # Omit block's header
            continue
        if "----" in line:     # Reached the end of one block
            break
        if isFirstInst == 1:
            addr = line[0:8]   # Get the start address of this block
            isFirstInst = 0
        block.append(line[0:-1]) # omit '\n'
    return (addr, block)


# Get all block from file
# Return a block list, each item comtains a basic block and its starting address
def GetBlocksFromFile(bblInst_file):
    #fileName = "bblInst.log"
    fileName = bblInst_file
    blocks = list()
    i = 0
    with open(fileName, "r") as f1:
        while True:
            bbl = GetOneBlock(f1)
            if len(bbl[1]) <= 0 or bbl[0] == "":    # Reached the end
                break
            blocks.append(bbl)
            # i += 1
            # if i == 7249:
            #     print "Reached the end"  # Just for debug
            # print "[%d]: Read to block [%s]!" % (i, bbl[0])  # Just for debug
    print "Read [%s] complited!" % fileName
    return blocks


# Instruction that 'sub esp, xxx', 'add esp, xxx', 'xor exx, exx' will be filted.
def SpecialCheck(inst):
    spec = ['sub esp', 'add esp']
    inst_lower = inst.lower()
    idx = 0
    ret = True
    cnt = len(spec)
    while idx < cnt:
        if spec[idx] in inst_lower:
            # print inst
            ret = False
            break
        idx += 1
    inst2 = inst_lower.split('|')[1]
    if 'xor' in inst2:
        p1 = inst2.split(' ')[1][0:-1]  # Remove ','
        p2 = inst2.split(' ')[2]
        if p1 == p2:    # Filter some reset instruction, just like :  xor eax, eax
            # print inst
            ret = False
    return ret


# Check for operator
def Check(inst):
    op = ['add', 'adc', 'sub', 'sbb', 'mul', 'div', 'shr', 'sar', 'shl', 'sal', 'rol', 'ror', 'rcl', 'rcr', 'xor', 'and', 'or', 'not']
    count = len(op)
    idx = 0
    ret = False
    if False == SpecialCheck(inst):  # For special demand
        return False
    inst_lower = inst.lower().split('|')[1].split(' ')[0]
    while idx < count:
        if op[idx] in inst_lower:  # Case in-sensitive
            ret = True
            break
        idx += 1
    return ret


# Count the arithmetic instruction rate in one block
def GetRate(bbl):
    instCnt = len(bbl)  # Tatol instruction count in block
    ArithmCnt = 0       # Arithmetic instruction count in block
    idx = 0
    rate = 0.0
    while idx < instCnt:
        inst = bbl[idx]
        res = Check(inst)  # Check funcion
        if res == True:
            ArithmCnt += 1
        idx += 1
    if instCnt > 0:
        rate = ArithmCnt * 1.0 / instCnt  # Convert to float point
    return (rate, ArithmCnt)


# Count the arithmetic instruction rate in each block
def CountArithmeticInstRate(bblInst_file):
    bbls = GetBlocksFromFile(bblInst_file)
    idx = 0;
    bblAddr = None
    bbl = None
    bblCount = len(bbls);
    bblResult = list()
    while idx < bblCount:
        (bblAddr, bbl) = bbls[idx]
        if bblAddr == "500682e9":
            pass
        (rate, arithmCnt) = GetRate(bbl)    # Get one block's rate
        tmp = (bblAddr, bbl, rate, arithmCnt)
        bblResult.append(tmp)
        idx += 1
    print "Count arithmetic instruction rate [%s] complited!" % bblInst_file
    return bblResult


# Output result to file
# bblStartAddress:ArithmeticInstructionRate
def OutputToFile(OutputFile, bblResult, minRate):
    with open(OutputFile, 'w') as f1:
        f2 = open("bblInst_Filter.log", 'w')
        bblCnt = len(bblResult)
        statisticResult = {}    # staticsti the result
        for i in xrange(11):
            statisticResult[i] = 0
        idx = 0
        while idx < bblCnt:
            data = bblResult[idx]
            bblAddr = data[0]
            bbl = data[1]
            rate = data[2]
            arithmCnt = data[3]

            rng = int(rate * 10)  # Convert to int
            if statisticResult.has_key(rng):
                statisticResult[rng] += 1
            else:
                statisticResult[rng] = 1

            if rate >= minRate and len(bbl) >= 8:  # Instruction count larger than 8
            # if rate >= minRate:  # Instruction count larger than 8
                fmt = "%s:%f\n" % (bblAddr, rate)
                f1.write(fmt)
            
            i = 0
            if rate >= minRate and len(bbl) >= 8: 
                fmt = "instcount:%d  mathinstcount:%d  mathrate:%f\n" % (len(bbl), arithmCnt, rate)
                f2.write(fmt)
                while i < len(bbl):
                    f2.write(bbl[i] + "\n")
                    i += 1
                f2.write("----\n")
            
            idx += 1
        f2.close()
        for i in xrange(10):
            res = statisticResult[i]
            fmt = "BBL math rate range from [%02d%%] to [%02d%%] has [%05d] block.\n" % (i*10, (i+1)*10, res)
            f1.write(fmt)
        fmt = "BBL math rate range from [%02d%%] to [%02d%%] has [%05d] block.\n" % (100, 100, statisticResult[10])
        f1.write(fmt)
        f1.write("\n")
    print "Output to file [%s] complited!" % OutputFile
    pass


# Main function
def Main():
    minRate = 0.2   # The threshold of arithmetic instruction rate
    bblResult = None
    bblInst_file = "bblInst.log"
    outputFileName = "ArithmeticInstructionRate.log"
    try:
        bblResult = CountArithmeticInstRate(bblInst_file)
        OutputToFile(outputFileName, bblResult, minRate)
        print "Finish!"
    except Exception as exp:
        print "Error: " + str(exp)
    input("Press any key to continue.")


Main()    



