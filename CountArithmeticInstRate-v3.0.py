
"""
Note:

This python script is to statistic the arithmetic instruction rate
from each block, and then output the statistic result to file.

[Python version]: Python 2.7

[Source file]:  bblInst.log          # Basic block set
[Output file1]: bblStatistic.log     # A brief result
[Output file1]: bblInst_Filter.log   # A detial result

                             Author: LongMai, root_mx@sjtu.edu.cn
                             Updata: 25/11/2017,  12:29PM

"""



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
        operand1 = inst2.split(' ')[1][0:-1]  # Remove ','
        operand2 = inst2.split(' ')[2]
        if operand1 == operand2:    # Filter some reset instruction, just like :  xor eax, eax
            # print inst
            ret = False
    return ret


# Check for operator
def Check(inst):
    op = ['add', 'adc', 'sub', 'sbb', 'mul', 'div', 'shr', 'sar', 'shl', 'sal', 'rol', 'ror', 'rcl', 'rcr', 'xor', 'and', 'or', 'not',
    'neg' # Add in version 2.1
    ]
    count = len(op)
    idx = 0
    ret = False
    if False == SpecialCheck(inst):  # For special demand
        return False
    opcode = inst.lower().split('|')[1].split(' ')[0]  # Eg.    inst = "1007aeb0|mov esi, edi"
    while idx < count:
        if op[idx] in opcode:  # Case in-sensitive
            ret = True
            break
        idx += 1
    return ret


# Count the arithmetic instruction rate in one block
def GetRateFromOneBlock(bbl):
    instCnt = len(bbl)  # Tatol instruction count in block
    ArithmCnt = 0       # Arithmetic instruction count in block
    idx = 0
    rate = 0.0
    while idx < instCnt:
        inst = bbl[idx]    # Get one instruction from block
        res = Check(inst)  # Check the instructioin whether is the arithmetic type
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
        (rate, arithmCnt) = GetRateFromOneBlock(bbl)       # Get one block's rate
        tmp = (bblAddr, bbl, rate, arithmCnt)  # Wrape data
        bblResult.append(tmp)
        idx += 1
    print "Count arithmetic instruction rate [%s] complited!" % bblInst_file
    return bblResult


# Output result to file
# bblStartAddress:ArithmeticInstructionRate
def OutputToFile(fileNameBriefe, fileNameDetail, bblResult, minRate, minInst):
    with open(fileNameBriefe, 'w') as f1:  # "bblStatistic.log"
        f2 = open(fileNameDetail, 'w')     # "bblInst_Filter.log"
        fmt = "%s: %s\n" % ("BlockAddr", "MathInstRate")
        f1.write(fmt)
        
        # Init the statistic result
        statisticResult = {}    
        for i in xrange(11):
            statisticResult[i] = 0
        
        bblCnt = len(bblResult)
        idx = 0
        while idx < bblCnt:
            data = bblResult[idx]
            bblAddr = data[0]
            bbl = data[1]
            rate = data[2]
            arithmCnt = data[3]

            # Statistic
            if len(bbl) >= minInst:
                rng = int(rate * 10)  # Convert to int
                if statisticResult.has_key(rng):
                    statisticResult[rng] += 1
                else:
                    statisticResult[rng] = 1
            
            # Output brief info
            if rate >= minRate and len(bbl) >= minInst:  # Instruction count larger than 8
            # if rate >= minRate:  # Instruction count larger than 8
                fmt = "%s : %f\n" % (bblAddr, rate)
                f1.write(fmt)
            
            # Output detail info
            i = 0
            if rate >= minRate and len(bbl) >= minInst: 
                fmt = "instcount:%d  mathinstcount:%d  mathrate:%f\n" % (len(bbl), arithmCnt, rate)
                f2.write(fmt)
                while i < len(bbl):
                    f2.write(bbl[i] + "\n")
                    i += 1
                f2.write("----\n")
            
            idx += 1   # End while

        f2.close()

        # Statistic total basic block
        fmt = "\nStatistic total basic block.:\n"
        f1.write(fmt)
        for i in xrange(10):
            res = statisticResult[i]
            fmt = "BBL math rate range : {[%3d%%] <= rate <  [%3d%%]} has [%5d] blocks.\n" % (i*10, (i+1)*10, res)
            f1.write(fmt)
        fmt = "BBL math rate range : {[%3d%%] <= rate <= [%3d%%]} has [%5d] blocks.\n" % (100, 100, statisticResult[10])
        f1.write(fmt)
        fmt = "Total BBK has [%5d] blocks.\n" % (bblCnt)
        f1.write(fmt)
        f1.write("\n")

    print "Output brief info to file [%s] complited!" % fileNameBriefe
    print "Output detail info to file [%s] complited!" % fileNameDetail


# Main function
def Main():
    minRate = 0.2   # The threshold of arithmetic instruction rate
    minInst = 8     # Just consider bbls which instructions larger than 8
    bblResult = None
    bblInst_file = "bblInst.log"
    outputFileNameBrief = "bblStatistic.log"
    outputFileNameDetail = "bblInst_Filter.log"
    try:
        bblResult = CountArithmeticInstRate(bblInst_file)
        OutputToFile(outputFileNameBrief, outputFileNameDetail, bblResult, minRate, minInst)
        print "Finish!"
    except Exception as exp:
        print "Error: " + str(exp)
    input("Press [Entry] to continue.")


Main()    



