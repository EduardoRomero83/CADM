import os
import sys

treeName = sys.argv[1]
dataset = sys.argv[2]

indir = "./ResearchData/" + dataset + "raw/"
outfile = "./ResearchData/" + dataset + "merged/" + treeName + ".data"
out = []

for f in sorted(os.listdir(indir)):
  if treeName in f:
    temp = indir + f
    content = open(temp, "r").readlines()
    out.append(f+"\n")
    out.extend(content)

with open(outfile, "w") as output:
  for line in out:
    output.write(line)
