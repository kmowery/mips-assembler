import re

class Register:
  names = [
      ["$0", "$zero"],
      ["$1", "$at"],
      ["$2", "$v0"],
      ["$3", "$v1"],
      ["$4", "$a0"],
      ["$5", "$a1"],
      ["$6", "$a2"],
      ["$7", "$a3"],
      ["$8", "$t0"],
      ["$9", "$t1"],
      ["$10", "$t2"],
      ["$11", "$t3"],
      ["$12", "$t4"],
      ["$13", "$t5"],
      ["$14", "$t6"],
      ["$15", "$t7"],
      ["$16", "$s0"],
      ["$17", "$s1"],
      ["$18", "$s2"],
      ["$19", "$s3"],
      ["$20", "$s4"],
      ["$21", "$s5"],
      ["$22", "$s6"],
      ["$23", "$s7"],
      ["$24", "$t8"],
      ["$25", "$t9"],
      ["$26", "$k0"],
      ["$27", "$k1"],
      ["$28", "$gp"],
      ["$29", "$sp"],
      ["$30", "$fp"],
      ["$31", "$ra"],
      ]
  def __init__(self, name=None, id=None):
    self.id = None
    if id is not None:
      self.id = id
    elif name is not None:
      for i,n in enumerate(self.names):
        if name.lower() in n:
          self.id = i
    else:
      raise "Give a register"
    if self.id is None:
      raise "Unknown register:" + name + id

  def binary(self):
    return self.id

  def __repr__(self):
    return "Register(%s)"%(self.names[self.id][1])


class UnusedRegister:
  def __init__(self):
    pass

  def binary(self):
    return 0

  def __repr__(self):
    return "NoRegister"

