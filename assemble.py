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
parser.add_argument('-d', '--data_base', default=0x4000,
    help="Base location of data", metavar="addr")
parser.add_argument('-o', '--output', default=argparse.SUPPRESS,
  help="Output file", metavar="filename")
parser.add_argument('-p', '--data_out', default=argparse.SUPPRESS,
    help="Output file for data section", metavar="filename")
parser.add_argument('-l', '--littleendian', default=False, action='store_true',
  help="Output as little endian")
parser.add_argument('-v', '--verbose', default=False, action='store_true',
  help="Be verbose")

args = vars(parser.parse_args())

f = open(args['filename'])
lines = f.readlines()
lines = [x.replace("\n", "") for x in lines]
f.close()

mp = mips.MIPSProgram(text_base=args['text_base'], data_base=args['data_base'])
mp.AddLines(lines)

output = open(args['output'], 'w') if 'output' in args else None
endianness = "little" if args['littleendian'] else "top"

if 'output' in args:
  with open(args['output'], 'w') as out:
    print "Writing text to '%s'..."%(args['output']),
    bytes = mp.Bytes(endian=endianness)
    for b in bytes:
      out.write("%c"%(b,))
  print "done!"

if 'data_out' in args:
  with open(args['data_out'], 'w') as out:
    print "Writing data to '%s'..."%(args['data_out']),
    for s in mp.data:
      out.write(s)
  print "done!"

if 'verbose' in args or 'output' not in args:
  binary = mp.Bytes(endian=endianness)
  for j in range(len(binary)/4):
    print "%02x %02x %02x %02x"%tuple(binary[j*4:j*4+4])

