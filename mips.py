import itertools
import re
import sys
import traceback

from instruction import Instruction
from register import Register, UnusedRegister

class MIPSProgram:
  def __init__(self, lines=None, text_base=0, data_base=0x4000):
    self.text_base = text_base if isinstance(text_base, int) else eval(text_base)
    self.data_base = data_base if isinstance(data_base, int) else eval(data_base)
    self.instructions = []
    self.data = []
    self.labels = {}
    self.defines = {}

    if lines is not None:
      self.AddLines(lines)


  def AddLines(self, lines):
    for l in lines:
      self.HandleLine(l)

  def HandleLine(self, line):
    loc = sum([x.Size() for x in self.instructions])

    for replace,value in self.defines.iteritems():
      line = re.sub(replace, value, line)

    if re.match("^\s*$", line) is not None:
      return

    try:
      m = re.match(
          r'''^\s*\.DEFINE\s*(?P<label>[_a-zA-Z0-9]+)\s*(?P<value>.*)$''',
          line)
      if m is not None:
        self.defines[m.group('label')] = m.group('value')
        return

      m = re.match(
          r'''^\s*\.STRING\s*(?P<label>[_a-zA-Z0-9]+)\s*(?P<str>".*")''',
          line)
      if m is not None:
        self.RegisterDataLabel(m.group('label'), eval(m.group('str')))
        return
      m = re.match("^\s*(?P<label>[_a-zA-Z0-9]+):\.*$", line)
      if m is not None:
        self.RegisterLabel(m.group('label'), loc)
        return
      m = re.match("^\s*#.*$", line)
      if m is not None:
        return

      inst = Instruction.parseline(self, loc, line)
      self.instructions.append(inst)
    except Exception as e:
      print
      print traceback.format_exc(e)
      print "*** Invalid line: '%s'"%(line)
      print
      sys.exit(1)

  def RegisterLabel(self, label, addr):
    self.labels[label] = addr

  def RegisterDataLabel(self, label, string):
    string = string + "\0"
    position = sum([len(x) for x in self.data])
    self.labels[label] = self.data_base + position
    self.data.append(string)

  # Returns the label position
  def Label(self, label):
    if hasattr(label, '__call__'):
      value = label()
      return  value
    if label not in self.labels.keys():
      raise Exception("Unknown label: '%s'"%(label))

    return self.labels[label]

  def Bytes(self, endian="big"):
    return list(itertools.chain( *[x.Bytes(endian=endian) for x
      in self.instructions] ))

