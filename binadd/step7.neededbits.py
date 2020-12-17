from bitarray import bitarray
import math
import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameter: python step7.neededbits.py treeName\n")
    exit()
treeName=sys.argv[1]

infile = "./binadd/tempFiles/" + treeName + ".secondhash.nodup.txt"

f = open(infile, "r")
lines = f.readlines()
f.close()

pathSizeFile = "./metadata/" + treeName + ".numpaths.txt"
f = open(pathSizeFile)
nums = f.readlines()
f.close()

finalNumBits = int(math.floor(math.log(int(nums[0]),2)) + 3)

code = {}
code['0'] = bitarray('0')
code['1'] = bitarray('1')

code2 = {}
code3 = {}

def revertEndian(word):
    half1 = word[-8:]
    half2 = word[:8]
    newstr = half1 + half2
    return newstr

def toBin2(l):
    global code2
    resps = [int(x) for x in l.split(",")]
    r = resps.index(max(resps))
    if r not in code2:
        num = bin(int(r))[2:].zfill(15)
        code2[r] = bitarray(num)

def toBin3(l):
    global code3
    resps = l.split(",")
    i = 0
    for n in resps:
        if n not in code3:
            if n == "0":
                num = bin(int(n))[2:].zfill(1)
            elif int(n) < 128:
                num = "10" + bin(int(n))[2:].zfill(7)
            else:
                num = "11" + bin(int(n))[2:].zfill(10)
            code3[int(n)] = bitarray(num)

def fillup(count):
    for i in range(count-1):
        b = bitarray(bin(0)[2:].zfill(160))
        global outfile
        global printedLines 
        printedLines = printedLines + 1
        b.tofile(outfile)

i = 1
prevaddr = -1
printedLines = 0
maxlen =  0
sumlen = 0
for line in lines:
    a = bitarray()
    conf, addr, resp, cID = line.strip().split()
    j = int(addr,2)
    prevaddr = j
    printedLines = printedLines + 1
    a.encode(code,conf)
    toBin2(resp)
    toBin3(resp)
    r = [int(x) for x in resp.split(',')]
    if conf == "0":
        a.encode(code2,[r.index(max(r))])
    else:
        a.encode(code3,r[:3])   
    sumlen = sumlen + len(a)
    if len(a) > maxlen:
        maxlen = len(a)
    #Signature byte
    signByte = bin((int(cID) % 255) + 1)[2:].zfill(8)
    b = bitarray(signByte)
    a.extend(b)
    i = i + 1

#print "Missed %d lines" %(2**(finalNumBits) - printedLines)
# While there are missed lines (probably at the end) append lines. o.w. problems when nothing hashes to 111...111
print(sumlen//len(lines))
print(maxlen)

