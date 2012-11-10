#!/usr/bin/env python

import argparse
import sys
import re

from mips import Register
from instruction import Instruction
import instruction

instructions = []

def handle_line(line):
  if re.match("^\s*$", line) is not None:
    return
  m = re.match("^\s*(?P<label>[a-zA-Z0-9]+):\.*$", line)
  if m is not None:
    Instruction.registerlabel(m.group('label'), len(instructions))
    return

  m = re.match("^\s*#.*$", line)
  if m is not None:
    return

  instructions.append(Instruction.parseline(len(instructions), line))


parser = argparse.ArgumentParser(description="A very small MIPS assembler.")
parser.add_argument('filename')
parser.add_argument('-b', '--base', default=argparse.SUPPRESS,
    help="Base location of code", metavar="addr")
parser.add_argument('-o', '--output', default=argparse.SUPPRESS,
  help="Output location", metavar="filename")
parser.add_argument('-l', '--littleendian', default=False, action='store_true',
  help="Output as little endian")

args = vars(parser.parse_args())

f = open(args['filename'])
lines = f.readlines()
f.close()

output = open(args['output'], 'w') if 'output' in args else None

if "base" in args:
  Instruction.setbaseaddress(eval(args['base']))

for l in lines:
  handle_line(l)

endianness = "little" if args['littleendian'] else "top"

if 'output' in args:
  with open(args['output'], 'w') as out:
    print "Writing to '%s'..."%(args['output']),
    for x in instructions:
      bytes = x.Bytes(endian=endianness)
      for b in bytes:
        out.write("%c"%(b,))
  print "done!"

else:
  binary = [x.Bytes(endian=endianness) for x in instructions]
  for i in binary:
    print "%02x %02x %02x %02x"%tuple(i)

