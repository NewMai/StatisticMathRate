




def GetRange(bblTraceFile, startAddr, endAddr):
    with open(bblTraceFile, 'r') as f1:
        startIdx = 0
        endIdx = 0
        startFlag = False
        TraceResult = []
        count = 0
        for line in f1:
            tmpAddr = line.split(':')[0].lower()
            if startFlag == False and startAddr in tmpAddr:
                startIdx = count
                startFlag = True
                print "Start address at %d" % startIdx
            elif startFlag == True and endAddr in tmpAddr:
                endIdx = count
                print "End address at %d" % endIdx
            ADDR = line.split(':')[0].lower()
            TraceResult.append(ADDR)      # Just use the address 
            # TraceResult.append(line.lower())
            count += 1
    print "Get range [%s]  from [%s] to [%s] complited!\n" % (bblTraceFile, startAddr, endAddr)
    return (startIdx, endIdx, TraceResult)


# Convert list to dict and remove redundancy
def GetRangeInSet(bblResult):
    startIdx = bblResult[0]
    endIdx = bblResult[1]
    bblTracingResult =  bblResult[2]
    # len1 = len(bblTracingResult)
    bblRes = bblTracingResult[startIdx:endIdx+1]
    bblTracingSet = set(bblRes)
    return bblTracingSet


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
    print "Read [%s] complited!\n" % fileName
    return blocks


def OutputbblTracingToFile(fileName, bblTracingSet):
    with open(fileName, 'w') as f1:
        for line in bblTracingSet:
            f1.write(line + "\n")
    print "Output to file [%s] complited!\n" % fileName


def FiltAndOutputBlocksToFile(fileName, bbls, bblTracingSet):
    with open(fileName, 'w') as f1:
        bblCnt = len(bbls)
        idx = 0
        addr = None
        while idx < bblCnt:
            bbl = bbls[idx][1]
            addr = bbls[idx][0].lower() 
            if addr in bblTracingSet:
                i = 0
                instCnt = len(bbl)
                while i < instCnt:
                    f1.write(bbl[i]+ "\n")
                    i += 1
                f1.write("----\n")  # End one block
                # print "Get block: %s\n" % addr
            idx += 1
    print "Output to file [%s] complited!\n" % fileName
    pass


# Main function
def Main():
    minRate = 0.55   # The threshold of arithmetic instruction rate
    bblResult = None
    bblTracing_file = "bblTracing.log"
    outputFileName = "bblTracing_Result.log"
    bblInstFlterFileName = "bblInst_Filter.log"
    bblInstFileName = "bblInst.log"
    startAddr = "5006636d"       # The range start address from bblTracing.log
    endAddr = "50066510"         # The range end address from bblTracing.log
    bblResult = None
    bblTracingSet = None
    bbls = None
    try:
        bblResult = GetRange(bblTracing_file, startAddr.lower(), endAddr.lower())
        bblTracingSet = GetRangeInSet(bblResult)
        if endAddr in bblTracingSet:
            print "%s in set." % endAddr
        else:
            print "%s not in set." % endAddr
        bbls = GetBlocksFromFile(bblInstFileName)
        FiltAndOutputBlocksToFile(bblInstFlterFileName, bbls, bblTracingSet)
        OutputbblTracingToFile(outputFileName, bblTracingSet)
        print "Finish!"
    except Exception as exp:
        print "Error: " + str(exp)
    input("Press any key to continue.\n")


Main()    





