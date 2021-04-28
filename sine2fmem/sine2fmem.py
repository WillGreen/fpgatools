#!/usr/bin/env python3

# sine2fmem.py - sine table generator for Verilog $readmemh format
# (C)2021 Will Green, open source software released under the MIT License
# For latest version and docs visit https://github.com/projf/fpgatools

from math import ceil, sin, pi
import sys

# math.sin works in radians
# 0-90° == π/2 radians

if (len(sys.argv) > 1):
    steps = int(sys.argv[1])
else:
    steps = 256

if (len(sys.argv) > 2):
    width = int(sys.argv[2])
else:
    width = 16

print("// Generated by sine2fmem.py from Project F")
print("// Learn more at https://github.com/projf/fpgatools")

fmt_width = str(ceil(width/4))  # four bits per hex digit
fmt_string = "{:0" + fmt_width + "X}  // {:03}: sin({:.4f}) = {:.4f}"

for i in range(steps):
    val = (pi/(2*steps)) * i
    res = sin(val)
    res_scaled = round((2**width-1) * res)
    print(fmt_string.format(res_scaled, i, val, res))
