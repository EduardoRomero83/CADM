from bitarray import bitarray
import math
import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameter: python step8.tobinary.py treeName\n")
    exit(1)
treeName=sys.argv[1]

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

infile = "./binadd/tempFiles/" + treeName + ".secondhash.nodup.txt"

f = open(infile, "r")
lines = f.readlines()
f.close()

pathSizeFile = "./metadata/" + treeName + ".numpaths.txt"
f = open(pathSizeFile)
nums = f.readlines()
f.close()

finalNumBits = int(math.floor(math.log(int(nums[0]),2)) + 3)

bitsLineFile = "./metadata/" + treeName + ".bitsperaddline.txt"
f = open(bitsLineFile)
nums = f.readlines()
f.close()

bitsperLine = 24
#print bitsperLine
bitspersignature = 8

#while (not (bitsperLine % 8)== 0) or not (((bitsperLine/8) % 6) == 0):
#    bitsperLine = bitsperLine + 1
#print bitsperLine
#a = bitarray()
code = {}
codea = {}
codeb = {}
code['0'] = bitarray('00000000')
codea['1'] = bitarray('10000000')
codeb['1'] = bitarray('10000001')

code2 = {}
code3 = {}
outfile = open("./metadata/" + treeName+ ".addresses.bin", "w+b")

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
        num = bin(int(r))[2:].zfill(16)
        code2[r] = bitarray(num)

def toBin3(l):
    global code3
    i = 0
    for n in l:
        if n not in code3:
            if n in primes:
                temp = primes.index(n)
                num = bin(temp)[2:].zfill(8)
                code3[n] = bitarray(num)

def fillup(count):
    for i in range(count-1):
        b = bitarray(bin(0)[2:].zfill(bitsperLine + bitspersignature))
        global outfile
        global printedLines 
        printedLines = printedLines + 1
        b.tofile(outfile)
#        print b

i = 1
prevaddr = -1
printedLines = 0
maxlen =  0
sumlen = 0
for line in lines:
    #if i % 10000 == 0:
        #print "%d/%d" %(i,len(lines))
    a = bitarray()
    conf, addr, resp, cID = line.strip().split()
    j = int(addr,2)
    if j != prevaddr + 1:
        fillup(j - prevaddr)
        #print "Printed %d" %(j-prevaddr-1)
    prevaddr = j
    printedLines = printedLines + 1
    r = [int(x) for x in resp.split(',')]
    toBin2(resp)
    toBin3(r)
    if conf == "0":
        a.encode(code,conf)
        a.encode(code2,[r.index(max(r))])
    elif r[1] > 0:
        a.encode(codea,conf)
        a.encode(code3,r[:1])
        a.encode(code3,r[1:2])
    else:
        a.encode(codeb,conf)
        a.encode(code3,r[:1])
        a.encode(code3,r[2:3])
    #while len(a) < bitsperLine:
        #a.encode(code,"0")
    #Signature byte
    signByte = bin((int(cID) % 255) + 1)[2:].zfill(bitspersignature)
    #signByte = revertEndian(signByte)
    b = bitarray(signByte)
    #print b
    a.extend(b)
    sumlen = sumlen + len(a)
   # if len(a) > maxlen:
    #    print line
#       maxlen = len(a)
    #print line
    #print a
    a.tofile(outfile)
    i = i + 1
    #if i > 1:
#       break

missedLines = (2**(finalNumBits) - printedLines + 1)
if (missedLines > 0):
    fillup(missedLines)

