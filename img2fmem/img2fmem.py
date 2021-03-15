#!/usr/bin/env python3

# img2fmem.py - image to FPGA memory map converter 2020 edition
# By Will Green - https://projectf.io
# (C)2021 Will Green, open source software released under the MIT License
# For latest version and docs visit https://github.com/projf/fpgatools

import os
import sys
from PIL import Image

if (len(sys.argv) != 4 and len(sys.argv) != 5):
    print("Convert image files to FPGA memory maps in $readmemh or Xilinx COE format.")
    print("usage: img2fmem.py image_file colour_bits output_format palette_bits")
    print("         image_file: source image file name")
    print("         colour_bits: number of colour index bits per pixel: 4, 6, or 8")
    print("         output_format: mem or coe")
    print("         palette_bits: number of palette bits: 12 (default) or 24")
    print("\nExample: img2fmem.py test.png 8 mem 24")
    sys.exit()

MESSAGE = "Generated by img2fmem.py from Project F - https://github.com/projf/fpgatools\n"

input_file = sys.argv[1]
base_name = os.path.splitext(input_file)[0]

colour_bits = int(sys.argv[2])
if colour_bits == 4:
    pal_size = 16
elif colour_bits == 6:
    pal_size = 64
else:
    pal_size = 256      # default to 8-bit
    colour_bits = 8     # explicitly assign a value so we can use in COE format

output_format = sys.argv[3]

palette_bits = 12       # default to 12 bit output (4 bits per colour) - as in 2018 version
if len(sys.argv) == 5:
    palette_bits = int(sys.argv[4])
    if palette_bits != 24:  # 24 bit output (8 bits per colour) 
        palette_bits = 12   # 12 bit output (4 bits per colour)

# load source image
source_img = Image.open(input_file)
prev_img = source_img.copy()  # take a copy for later preview process
(width, height) = source_img.size
pixels = source_img.load()

# Reduce to 12-bit precision (4-bit per colour) in range 0-15 if required
if (palette_bits == 12): 
    for x in range(width):
        for y in range(height):
            pixels[x, y] = tuple([p // 16 for p in pixels[x, y]])

# Convert to limited colour palette
dest_img = source_img.convert('P', palette=Image.ADAPTIVE, colors=pal_size)
dest_pal = dest_img.palette.palette

# Generate hex image output
image_data = dest_img.getdata()
image_output = ''
if output_format == 'mem':
    image_output += "// " + MESSAGE
    for d in image_data:
        image_output += "{:02X}\n".format(d)
elif output_format == 'coe':
    image_output += "; " + MESSAGE
    image_output += "memory_initialization_radix={:d};\n".format(colour_bits)
    image_output += "memory_initialization_vector=\n"
    for d in image_data:
        image_output += "{:02X},\n".format(d)
    # replace last comma with semicolon to complete coe statement
    image_output = image_output[:-2]
    image_output += ";\n"
else:
    print("Error: output_format should be mem or coe.")
    sys.exit()

with open(base_name + '.' + output_format, 'w') as f:
    f.write(image_output)

# Chunk raw palette into three byte sections (RGB)
colours = [bytearray(dest_pal[i:i+3]) for i in range(0, len(dest_pal), 3)]

# Generate hex palette output
palette_output = ''
if output_format == 'mem':
    palette_output += "// " + MESSAGE
    for i in range(pal_size):
        if (palette_bits == 24):
            pal_entry = colours[i][0] * 2**16 + colours[i][1] * 2**8 + colours[i][2]
            palette_output += "{:06X}\n".format(pal_entry)
        else:
            pal_entry = colours[i][0] * 2**8 + colours[i][1] * 2**4 + colours[i][2]
            palette_output += "{:03X}\n".format(pal_entry)
elif output_format == 'coe':
    palette_output += "; " + MESSAGE
    palette_output += "memory_initialization_radix={:d};\n".format(palette_bits)
    palette_output += "memory_initialization_vector=\n"
    for i in range(pal_size):
        if (palette_bits == 24):
            pal_entry = colours[i][0] * 2**16 + colours[i][1] * 2**8 + colours[i][2]
            palette_output += "{:06X},\n".format(pal_entry)
        else:
            pal_entry = colours[i][0] * 2**8 + colours[i][1] * 2**4 + colours[i][2]
            palette_output += "{:03X},\n".format(pal_entry)
    # replace last comma with semicolon to complete coe statement
    palette_output = palette_output[:-2]
    palette_output += ";\n"
else:
    print("Error: output_format should be mem or coe.")
    sys.exit()

with open(base_name + '_palette.' + output_format, 'w') as f:
    f.write(palette_output)

# Convert preview image and save
# If using 12-bit palette retain full 0-255 range so preview image is not too dark
prev_pixels = prev_img.load()
if (palette_bits == 12): 
    for x in range(width):
        for y in range(height):
            prev_pixels[x, y] = tuple([(p // 16) * 16 for p in prev_pixels[x, y]])
prev_img = prev_img.convert('P', palette=Image.ADAPTIVE, colors=pal_size)
prev_img.save(base_name + '_preview.png')
