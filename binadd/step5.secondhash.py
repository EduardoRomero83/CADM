import math
import sys

if (len(sys.argv) != 3):
    print("This command takes 2 parameter: python step5.secondhash.py treeName numClasses\n")
    exit()
treeName=sys.argv[1]
numClasses=int(sys.argv[2])

infile = "./binadd/tempFiles/" + treeName + ".firsthash.combinedconflicts.txt"

f = open(infile, "r")
lines = f.readlines()
f.close()

pathSizeFile = "./metadata/" + treeName + ".numpaths.txt"
f = open(pathSizeFile)
nums = f.readlines()
f.close()

finalNumBits = int(math.floor(math.log(int(nums[0]),2)) + 3)

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 183, 193, 197, 199,
211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293,
307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397,
401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499,
503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599,
601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691,
701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797,
809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887,
907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]


def dohash(addr, cID, adSet, adSize, n1, n2):
    newaddr = ((n1 * addr) + (n2 * cID)) % adSize
    if newaddr not in adSet:
        return newaddr
    else:
        return adSize

def dohashPlanB(addr, cID, adSet, adSize, n1, n2):
    newaddr = (n1 * (addr + n2 + cID) ) % adSize
    if newaddr not in adSet:
        return newaddr
    else:
        return adSize



def createRes(n1, n2):
    toRet = str(n1) + "," + str(n2) + ",0"*(numClasses-2)
    return toRet

def createResB(n1, n2):
    toRet = str(n1) + ",0," + str(n2) + ",0"*(numClasses-1)
    return toRet


def combineResps(r1, r2):
    #print r1
    #print r2
    #print "Fail here"
    #exit()
    l1 = [int(x) for x in r1.split(",")]
    l2 = [int(x) for x in r2.split(",")]
    l3 = [l1[i] + l2[i] for i in range(len(l1))]
    toRet = ""
    for num in l3[:-1]:
        toRet = toRet + str(num) + ","
    return toRet + str(l3[-1])

def combineListofResps(resplist):
    curresp = "0" + ",0"*(numClasses-1) # number of 0s = number of classifications
    for resp in resplist:
        curresp = combineResps(curresp, resp)
    return curresp

def fixImpossible(addrs, resps, cIDs, addrSet):
    uniquepaths = {}
    for i in range(len(addrs)):
        if cIDs[i] not in uniquepaths:
            uniquepaths[cIDs[i]] = [[addrs[i], resps[i], cIDs[i]]]
        else:
            uniquepaths[cIDs[i]].append([addrs[i], resps[i], cIDs[i]])
    newblock = []
    removedDuplicate = False
    for key in uniquepaths:
        if len(uniquepaths[key]) > 1:
            removedDuplicate = True
            #print "ERROR"
            #exit()
            respstocombine = []
            current = uniquepaths[key]
            for l in current:
                respstocombine.append(l[1])
            newList = [current[0][0], combineListofResps(respstocombine) ,current[0][2]]
            uniquepaths[key] = [newList]
        current = uniquepaths[key]
        newstr = current[0][0] + " " + current[0][1] + " " + current[0][2]
        newblock.append(newstr)
    if len(newblock) == 1:
        newblock[0] = "0 " + newblock[0]
        return newblock, removedDuplicate
    for i in range(len(newblock)):
        newblock[i] = "1 " + newblock[i]
    return newblock, removedDuplicate

def hashFailedGroup(addrs, cIDs, addrSet):
    addr = [int(x,2) for x in addrs]
    cID = [int(x) for x in cIDs]
    adSize = 2**finalNumBits
    for i in primes:
        for j in range(2**12):
            adSet = []
            for k in range(len(addr)):
                newaddr = dohashPlanB(addr[k], cID[k], addrSet, adSize, i, j)
                if newaddr == adSize or newaddr in adSet:
                    break
                adSet.append(newaddr)
            if len(adSet) == len(addr):
                return adSet, i, j
    return [], -1, -1

    
# Try hashing with any combination of primes
def hashGroup(addrs, cIDs, addrSet):
    addr = [int(x,2) for x in addrs]
    cID = [int(x) for x in cIDs]
    adSize = 2**finalNumBits
    for i in primes:
        for j in primes:
            adSet = []
            for k in range(len(addr)):
                newaddr = dohash(addr[k], cID[k], addrSet, adSize, i, j)
                if newaddr == adSize or newaddr in adSet:
                    break
                adSet.append(newaddr)
            if len(adSet) == len(addr):
                return adSet, i, j
    return [], -1, -1

#Handle conflicts
def divideConflict(blocks, addrSet):
    confs = []
    addrs = []
    resps = []
    cIDs = []
    primeList = ""
    #Read all lines in conflict into arrays
    for block in blocks:
        conf, addr, resp, cID = block.strip().split()
        confs.append(conf)
        addrs.append(addr)
        resps.append(resp)
        cIDs.append(cID)
    # Get new address and the two primes
    newaddr, n1, n2 = hashGroup(addrs, cIDs, addrSet)
    # Hash failed
    if n1 == -1:
        # Check if it was intra-cluster conflict
        newblock, fixedSomething = fixImpossible(addrs, resps, cIDs, addrSet)
        if len(newblock) == 1:
            #print "Is this what I did not add?"
            addrSet.add(int(newblock[0].split()[1], 2))
            #exit()
            return newblock[0]
        # No intra-cluster conflict, bigger problem
        if not fixedSomething:
            newaddr, n1, n2 = hashFailedGroup(addrs, cIDs, addrSet)
            if n1 == -1:
                print("ERROR AGAIN")
                exit()
            primeList = createResB(n1, n2)
        # Recursive call but no intra-cluster conflict now
        else:
            return divideConflict(newblock, addrSet)
    # Replace result with primes used for re-hashing
    if primeList == "":
        primeList = createRes(n1, n2)
    toRet = ""
    # Build lines to print in appropriate format
    for i in range(len(blocks)):
        conf, addr, resp, cID = blocks[i].strip().split()
        toRet = toRet + conf + " " + addr + " " + primeList + " " + cID + "\n"
        binaddr = bin(newaddr[i])[2:].zfill(finalNumBits)
        addrSet.add(newaddr[i])
        toRet = toRet + "0 " + binaddr + " " + resp + " " + cID
        if i < len(blocks) -1:
            toRet = toRet + "\n"
    return toRet


addrSet = set()

# Main

#Add features to set
for line in lines:
    conf, addr, rest = line.split(" ",2)
    addr = int(addr,2)
    addrSet.add(addr)

#Read lines
#If no conflict print
#Otherwise call divide conflict
for line in lines:
    conf, rest = line.split(" ", 1)
    if conf == "0":
        print(line.strip())
    else:
        blocks = line.strip().split(" $ ")
        print(divideConflict(blocks, addrSet))
