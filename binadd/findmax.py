import math
f = open("secondhash.sorted.nodup.txt", "r")
lines = f.readlines()
f.close()

maxN = 0
maxI = 0

for line in lines:
    c, a, resp, cid = line.split()
    idc = int(cid)
    nums = [int(x) for x in resp.split(",")]
    m = max(nums)
    if m > maxN:
        maxN = m
    if idc > maxI:
        maxI = idc

print maxN
print math.floor(math.log(maxN,2)) + 1
print maxI
print math.floor(math.log(maxI,2)) + 1

