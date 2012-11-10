import itertools
import re

from instruction import Instruction
from register import Register, UnusedRegister

class MIPSProgram:
  def __init__(self, lines=None, text_base=0):
    self.text_base = text_base
    self.instructions = []
    self.labels = {}

    if lines is not None:
      self.AddLines(lines)


  def AddLines(self, lines):
    for l in lines:
      self.HandleLine(l)

  def HandleLine(self, line):
    loc = sum([x.Size() for x in self.instructions])

    if re.match("^\s*$", line) is not None:
      return
    m = re.match("^\s*(?P<label>[a-zA-Z0-9]+):\.*$", line)
    if m is not None:
      self.RegisterLabel(m.group('label'), loc)
      return
    m = re.match("^\s*#.*$", line)
    if m is not None:
      return

    inst = Instruction.parseline(self, loc, line)
    self.instructions.append(inst)

  def RegisterLabel(self, label, addr):
    self.labels[label] = addr

  # Returns the label position
  def Label(self, label):
    return self.labels[label]

  def Labels(self):
    return self.labels.keys()

  def Bytes(self, endian="big"):
    return list(itertools.chain( *[x.Bytes(endian=endian) for x in self.instructions] ))

