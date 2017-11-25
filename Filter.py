

# Save suspicious operation involve algorithom
def GetSuspectOpSet():
    setOp = set()       # An operation set
    #setOp.add("xor")
    setOp.add("mul")
    setOp.add("imul")
    setOp.add("div")
    setOp.add("idiv")
    #setOp.add("add")
    #setOp.add("adc")
    #setOp.add("sub")
    #setOp.add("sbb")
    # Add additional intrunction here to filter.
    return setOp


# Get op code from an instruction
def GetOpCode(inst):
    op = inst.split(" ")
    op = op[0]
    return op


# Filter specific instruction , For example: xor eax, eax
# This instrunction is not involved to algrithom
# So, it should be excluded
def IsResetInst(inst):
    ret = False
    try:
        arg1 = inst[13:16]
        arg2 = inst[18:21]
        if arg1 == arg2:    # For example:  xor eax, eax
            ret = True
    except Exception as exp:
        pass
    return ret


# Filtering adjust stack instruction
def IsAdjustStack(inst):
    ret = False
    feature1 = "sub esp, "
    feature2 = "add esp, "
    if feature1 in inst:  
        ret = True
    if feature2 in inst:  
        ret = True
    return ret


# Check a block, whether include suspiciours instruction
# Return True, if it included,
# Otherwise return False
def CheckOneBlock(block):
    setOp = GetSuspectOpSet()
    len1 = len(block)
    flag = False
    lstContainer = list()

    for i in range(0, len1):
        inst = block[i]
        inst = inst.lower()
        op = GetOpCode(inst[9:])
        if op in setOp:
            if op == "xor" and True == IsResetInst(inst):   # Filter xor eax, eax, and so on
                continue  # Omit special xor instrunction which just reset a register
            if op == "sub" and True == IsAdjustStack(inst):
                continue  # Omit sub esp, xxx instruction
            if op == "add" and True == IsAdjustStack(inst):
                continue  # Omit add esp, xxx instruction
            flag = True
            lstContainer.append(op)  # Add this operation to list
        pass
    return (flag, lstContainer)


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


# Get block counter of execution times
# Return a dict
def GetBlockCounter(bbl_file):
    #fileName = "bbl.txt"
    fileName = bbl_file
    dictBlockCounter = dict()
    with open(fileName, "r") as f1:
        for line in f1:
            addr = line[0:8]            # Address
            counter = line[10:-1]       # Counter
            counter = int(counter)      # Convert to integer
            if dictBlockCounter.has_key(addr):
                dictBlockCounter[addr] += counter  # If an item has been in this dict, then add it
            else:
                dictBlockCounter[addr] = counter
    print "Read [%s] complited!" % fileName
    return dictBlockCounter


# Filter all baisc block
# Return a list, containing the suspicious block
def FilterSuspectBlock(bblInst_file, bbl_file):
    blocks = GetBlocksFromFile(bblInst_file)
    dictBlockCounter = GetBlockCounter(bbl_file)
    len1 = len(blocks)
    result = list()
    debug_i = 0
    fd = open("Error.log", "w")   # Log error
    for i in range(1, len1):
        bbl = blocks[i]
        ret_tmp = CheckOneBlock(bbl[1])
        isSuspicious = ret_tmp[0]
        if True == isSuspicious:   # Suspicious block, stored it
            try:
                counter = dictBlockCounter[bbl[0]]  # Get this basic block executed times
                result.append((bbl[0], counter, bbl[1], ret_tmp[1]))
            except Exception as exp:
                debug_i += 1
                log = "[%04dth]: Block [%s] is not in dict!\n" % (debug_i, bbl[0])
                fd.write(log)
    fd.close()
    print "Filter basic block complited!"
    return result


# Output the result to file
def OutputToFile(blocks):
    fileName = "FilterResult.log"
    fileName2 = "Summary.log"
    with open(fileName, "w") as f1:
        f2 = open(fileName2, "w")
        len1 = len(blocks)
        i = 0
        while i < len1:
            blk = blocks[i]
            i += 1
            var = "[Order: %03d]" % (i)
            f1.write(var + "\n")
            f2.write(var + "   ")

            opLst = blk[3]    # Output an op list
            opLst = list(set(opLst))  # Reduce redundency
            j = 0
            len2 = len(opLst)
            var = ""
            while j < len2:
                var += "[%s]" % (opLst[j])
                j += 1
            f1.write(var + "\n")
            f2.write(var + "   ")

            addr = blk[0]     # Output block's counter of execution
            counter = blk[1]
            body = blk[2]     # A basic block's body
            var = "[%s:%d]" % (addr, counter)
            f1.write(var + "\n")
            f2.write(var)

            j = 0            # Output a basic block
            len2 = len(body)
            var = ""
            while j < len2:
                var += body[j] + "\n"
                j += 1
            f1.write(var + "\n")
            f2.write("\n")

    f2.close()
    print "Output the result to [%s] completed!" % fileName
    print "Output the result's summary to [%s] completed!" % fileName2


# Main function
def Main():
    bblInst_file = "bblInst.log"
    bbl_file = "bblTracing.log"
    try:
        blocks = FilterSuspectBlock(bblInst_file ,bbl_file)
        OutputToFile(blocks)
        print "Finish!"
    except Exception as exp:
        print "Error: " + str(exp)
    input("Press any key to continue.")


Main()    




