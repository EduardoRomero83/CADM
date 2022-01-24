from bitarray import bitarray
import sys

if (len(sys.argv) != 3):
    print("This command takes 2 parameters: python step2.featToBin.py treeName mpc \n")
    exit(1)
treeName=sys.argv[1]
mpc = int(sys.argv[2])

f = open("./binfeats/commonandimp/" + treeName + ".commonandimp.txt", "r")
lines = f.readlines()
f.close()


code = {}
outfile = open("./metadata/" + treeName + ".features.bin", "w+b")

def revertEndian(word):
    half1 = word[-16:]
    half2 = word[:16]
    quart1 = half1[-8:]
    quart2 = half1[:8]
    quart3 = half2[-8:]
    quart4 = half2[:8]    
    #print quart1 + "  " + quart2 + " orig " + half1
    newstr = quart1 + quart2 + quart3 + quart4
    return newstr


def toBin(feats):
    global code
    for f in feats:
        if f not in code:
            #print(f)
            num = bin(int(f))[2:]
            #print(num)
            if len(num) < 8:
                num = num.zfill(8)
                num = num.ljust(16, "0")
            elif len(num) == 8:
                num = num.ljust(16, "0")
            else:
                num = num.zfill(16)
                tempNum = num[-8:]
                part2 = num[:8]
                num = tempNum + part2
            #print(num)
            code[f] = bitarray(num)

i = 1
print("start features.bin file")
for line in lines:
    #if (i % 10000 == 0):
    #    print "%d/%d" %(i,len(lines))
    #print line
    a = bitarray()
    try:
        cID, feats, imp, common = line.strip().split()
    except:
        print(line)
        exit()
    feats = feats.split(",")
    fID = [x[:3] for x in feats]
    vals = [x[3:] for x in feats]
    dividedFeats = [val for pair in zip(fID,vals) for val in pair]
    while(len(dividedFeats) < (2 * mpc)):
        dividedFeats.append("000")
    while(len(imp) < mpc):
        imp = imp + "0"
        common = common + "0"
    imp = imp.zfill(32)
    common = common.zfill(32)
    imp = revertEndian(imp)
    common = revertEndian(common)
    toBin(dividedFeats)
    #a.encode(code,dividedFeats)
    # Start of signature byte
    sign = bin((int(cID) % 255) + 1)[2:].zfill(32)
    sign = revertEndian(sign)
    c = bitarray(sign)
    # End of signature byte
    a.encode(code, dividedFeats)
    # a.tofile(outfile)
    b = bitarray(imp + common)
    a.extend(b)
    c.extend(a) #Changed this an following line to force signature at front
    c.tofile(outfile)
    i = i + 1
    #print cID
    #print c
    #if i > 1:
#   break

outfile.close()
