import csv
import os
#import sys

#treeName = sys.argv[1]

indir = "./ResearchData/merged/"
outfile = "./ResearchData/combined.csv"
out = []

filesToFind = ["acc.py", "time.txt", "acc.s", "pythonperf", "0.serverperf", "1.serverperf"]

def makeHeader():
  header = ["Number of trees", "max depth", "max per cluster", "max unknown"]
  header.extend(["python exec time", "server exec time", "python acc", "server acc"])
  header.extend(["cycles py", "cycles server m0", "cycles server m1"])
  header.extend(["instructions py", "instructions server m0", "instructions server m1"])
  header.extend(["branches py", "branches server m0", "branches server m1"])
  header.extend(["branch misses py", "branch misses server m0", "branch misses server m1"])
  header.extend(["branch miss % py", "branch miss % server m0", "branch miss % server m1"]) 
  header.extend(["cache lookups py", "cache lookups server m0", "cache lookups server m1"])
  header.extend(["cache misses py", "cache misses server m0", "cache misses server m1"])
  header.extend(["cache miss % py", "cache miss % server m0", "cache miss % server m1"]) 
  header.extend(["L1 lookups py", "L1 lookups server m0", "L1 lookups server m1"])
  header.extend(["L1 misses py", "L1 misses server m0", "L1 misses server m1"])
  header.extend(["L1 miss % py", "L1 miss % server m0", "L1 miss % server m1"]) 
  header.extend(["LLC lookups py", "LLC lookups server m0", "LLC lookups server m1"])
  header.extend(["LLC misses py", "LLC misses server m0", "LLC misses server m1"])
  header.extend(["LLC miss % py", "LLC miss % server m0", "LLC miss % server m1"]) 
  return header

def findSubstr(l, substr):
    for i, s in enumerate(l):
        if substr in s:
              return i
    return -1

def findManySubstr(l, substr):
    for i, s in enumerate(l):
        if all (x in s for x in substr):
              return i
    return -1

def findLims(l):
  global filesToFind
  slices = []
  lims = []
  failed = []
  for segment in filesToFind:
    temp = findSubstr(l, segment)
    if temp == -1:
      failed.append(segment)
      continue
    lims.append(temp)
  slims = sorted(lims)
  i = 0
  for seg in filesToFind:
    if seg in failed:
      slices.append([-1,-1])
      continue
    if lims[i] == slims[-1]:
      slices.append([lims[i], len(l)])
    else:
      slices.append([lims[i], slims[slims.index(lims[i]) + 1]])
    i = i + 1
  return slices

def findAccPy(l, row):
  global header
  temp = findSubstr(l, "Acc")
  acc = l[temp].split(":")[1]
  time = l[temp + 1]
  row[findSubstr(header,"python acc")] = float(acc)
  row[findSubstr(header, "python exec")] = float(time)

def findServTime(l, row):
  global header
  time = l[findSubstr(l,"Total")].split(':')[1]
  row[findSubstr(header, "server exec")] = float(time)

def findServAcc(l, row):
  global header
  acc = l[1].split(":")[1]
  row[findSubstr(header, "server acc")] = float(acc) 

def findPerf(l, row, model):
  global header
  var = "cycl"
  cycles = l[findSubstr(l,var)].split(",")
  ind = findManySubstr(header, [var, model])
  row[ind] = int(cycles[0])
  var = "inst" 
  inst = l[findSubstr(l,var)].split(",")
  ind = findManySubstr(header, [var, model])
  row[ind] = int(inst[0]) 
  stats = ["branch", "cache", "L1", "LLC"] 
  for var in stats:
    br = l[findSubstr(l,var)].split(",")
    ind = findManySubstr(header, [var, model])
    row[ind] = int(br[0]) 
    names = [var, "miss", model, "%"] 
    line = l[findManySubstr(l,names[0:2])].split(",")
    total = line[0]
    percent = line[len(line) -2]
    ind1 = findManySubstr(header, names[0:3])
    ind2 = findManySubstr(header, names)
    row[ind1] = int(total)
    row[ind2] = float(percent) 

def populateRow(segment, l, row):
  global filesToFind
  if len(l) == 0:
    return
  if segment == filesToFind[0]:
    return findAccPy(l, row)
  elif segment == filesToFind[1]:
    return findServTime(l, row)  
  elif segment == filesToFind[2]:
    return findServAcc(l, row)
  elif "python" in segment:
    return findPerf(l, row, "py")
  elif "0" in segment:
    return findPerf(l, row, "server m0")
  else:
    return findPerf(l, row, "server m1")

with open(outfile, "w") as csvfile:
  c = csv.writer(csvfile)
  header = makeHeader()
  c.writerow(header)
  for f in sorted(os.listdir(indir)):
    row = ["_" for i in range(len(header))]
    nameData = f.split(".")
    row[0:4] = [int(x) for x in nameData[1:-1]]
    temp = indir + f
    content = open(temp, "r").readlines()
    delims = findLims(content)
    for i in range(len(filesToFind)):
      try:
        populateRow(filesToFind[i], content[delims[i][0]:delims[i][1]], row) 
      except:
        pass
    c.writerow(row)
