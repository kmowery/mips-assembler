#!/usr/bin/env python

import argparse
import sys
import re


import mips
from register import Register
from instruction import Instruction
import instruction

parser = argparse.ArgumentParser(description="A very small MIPS assembler.")
parser.add_argument('filename')
parser.add_argument('-t', '--text_base', default=0,
    help="Base location of code", metavar="addr")
parser.add_argument('-o', '--output', default=argparse.SUPPRESS,
  help="Output location", metavar="filename")
parser.add_argument('-l', '--littleendian', default=False, action='store_true',
  help="Output as little endian")

args = vars(parser.parse_args())

f = open(args['filename'])
lines = f.readlines()
f.close()

mp = mips.MIPSProgram(text_base=args['text_base'])
mp.AddLines(lines)

output = open(args['output'], 'w') if 'output' in args else None
endianness = "little" if args['littleendian'] else "top"

if 'output' in args:
  with open(args['output'], 'w') as out:
    print "Writing to '%s'..."%(args['output']),
    bytes = mp.Bytes(endian=endianness)
    for b in bytes:
      out.write("%c"%(b,))
  print "done!"

else:
  binary = mp.Bytes(endian=endianness)
  for j in range(len(binary)/4):
    print "%02x %02x %02x %02x"%tuple(binary[j*4:j*4+4])

