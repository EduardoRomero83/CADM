import os
import sys

treeName=sys.argv[1]

f = open("paths/numericPaths/"+treeName+".numericPaths.txt", "r")
lines = f.readlines()
f.close()
lines.sort();

print(lines)
