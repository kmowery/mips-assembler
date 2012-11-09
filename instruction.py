import re

from mips import Register, UnusedRegister

instruction_types = [
  # add $0, $0, $0
  re.compile(r"^[^#]*?"
              "(?P<name>[a-zA-Z]+)\s*"
              "(?P<rd>\$[0-9a-zA-Z]+)\s*,\s*"
              "(?P<rs>\$[0-9a-zA-Z]+)\s*,\s*"
              "(?P<rt>\$[0-9a-zA-Z]+)"),


  # addi $t0, $t0, 0x1
  re.compile(r"^[^#]*?"
              "(?P<name>[a-zA-Z]+)\s*"
              "(?P<rt>\$[0-9a-zA-Z]+)\s*,\s*"
              "(?P<rs>\$[0-9a-zA-Z]+)\s*,\s*"
              "(?P<imm>[x0-9A-Fa-f]+)"),

  # beq $t0, $0, main
  re.compile(r"^[^#]*?"
              "(?P<name>[a-zA-Z]+)\s*"
              "(?P<rd>\$[0-9a-zA-Z]+)\s*,\s*"
              "(?P<rs>\$[0-9a-zA-Z]+)\s*,\s*"
              "(?P<label>[0-9a-zA-Z]+)"),

  # j main
  re.compile(r"^[^#]*?"
              "(?P<name>j[al]*)\s*"
              "(?P<label>[0-9a-zA-Z]+)"),

  # jr $0
  re.compile(r"^[^#]*?"
              "(?P<name>jr)\s*"
              "(?P<rs>\$[0-9a-zA-Z]+)"),

  # lbu $t0, 0x04($0)
  re.compile(r"^[^#]*?"
              "(?P<name>[a-zA-Z]+)\s*"
              "(?P<rt>\$[0-9a-zA-Z]+)\s*,\s*"
              "(?P<imm>[x0-9A-Fa-f]+)\s*"
              "\(\s*(?P<rs>\$[0-9a-zA-Z]+\s*)\)\s*"),

  # lui $t0, 0x8403
  re.compile(r"^[^#]*?"
              "(?P<name>[a-zA-Z]+)\s*"
              "(?P<rt>\$[0-9a-zA-Z]+)\s*,\s*"
              "(?P<imm>[x0-9A-Fa-f]+)\s*"),
]

r_type = {
  "add":     (0x0,0b100000),
  "addu":    (0x0,0b100001),
  "and":     (0x0,0b100100),
  "break":   (0x0,0b001101),
  "div":     (0x0,0b011010),
  "divu":    (0x0,0b011011),
  "jalr":    (0x0,0b001001),
  "jr":      (0x0,0b001000),
  "mfhi":    (0x0,0b010000),
  "mflo":    (0x0,0b010010),
  "mthi":    (0x0,0b010001),
  "mtlo":    (0x0,0b010011),
  "mult":    (0x0,0b011000),
  "multu":   (0x0,0b011001),
  "nor":     (0x0,0b100111),
  "or":      (0x0,0b100101),
  "sll":     (0x0,0b000000),
  "sllv":    (0x0,0b000100),
  "slt":     (0x0,0b101010),
  "sltu":    (0x0,0b101011),
  "sra":     (0x0,0b000011),
  "srav":    (0x0,0b000111),
  "srl":     (0x0,0b000010),
  "srlv":    (0x0,0b000110),
  "sub":     (0x0,0b100010),
  "subu":    (0x0,0b100011),
  "syscall": (0x0,0b001100),
  "xor":     (0x0,0b100110),
}

i_type = {
  "addi":  (0b001000,),
  "addiu": (0b001001,),
  "andi":  (0b001100,),
  "beq":   (0b000100,),
  "bgez":  (0b000001,0b00001),
  "bgtz":  (0b000111,0b00000),
  "blez":  (0b000110,0b00000),
  "bltz":  (0b000001,0b00000),
  "bne":   (0b000101,),
  "lb":    (0b100000,),
  "lbu":   (0b100100,),
  "lh":    (0b100001,),
  "lhu":   (0b100101,),
  "lui":   (0b001111,),
  "lw":    (0b100011,),
  "lwc1":  (0b110001,),
  "ori":   (0b001101,),
  "sb":    (0b101000,),
  "slti":  (0b001010,),
  "sltiu": (0b001011,),
  "sh":    (0b101001,),
  "sw":    (0b101011,),
  "sc":    (0b111000,),
  "swc1":  (0b111001,),
  "xori":  (0b001110,),
}

j_type = {
"j":       (000010,),
"jal":     (000011,),
}

labels = {}

# Sometimes we will consider imm to be shamt.
class Instruction:
  def __init__(self, name=None, rs=None, rt=None,
                     rd=None, imm=None,
                     label=None):
    if name.lower() not in r_type.keys() and \
       name.lower() not in i_type.keys() and \
       name.lower() not in j_type.keys():
      raise Exception("'%s' is not a MIPS opcode"%(name.lower()))
    self.name = name.lower()
    self.rs = Register(rs) if rs is not None else UnusedRegister()
    self.rt = Register(rt) if rt is not None else UnusedRegister()
    self.rd = Register(rd) if rd is not None else UnusedRegister()
    self.imm = eval(imm) if imm is not None else 0
    print imm, self.imm
    self.label = label

  @staticmethod
  def registerlabel(label, addr):
    labels[label] = addr

  @staticmethod
  def parseline(line):
    global instruction_types
    for t in instruction_types:
      m = t.match(line)
      if m is not None:
        return Instruction(**m.groupdict())
    raise Exception("'%s' not an instruction"%(line))

  def ToBinary(self):
    # TODO: deal with labels
    if self.name in r_type.keys():
      print (self.rs.binary() << 21)
      print self.rt.binary() << 16
      print self.rd.binary() << 11
      print self.imm << 6
      print r_type[self.name][1] << 0

      b = 0                            # opcode
      b |= (self.rs.binary() << 21)    # rs
      b |= (self.rt.binary() << 16)    # rt
      b |= (self.rd.binary() << 11)    # rd
      b |= (self.imm << 6)             # imm
      b |= (r_type[self.name][1] << 0) # funct
      return b

    if self.name in i_type.keys():
      print i_type[self.name][0]
      print self.rs
      print self.rt
      b = i_type[self.name][0] << 26 # opcode
      b |= (self.rs.binary() << 21) # rs
      b |= (self.rt.binary() << 16) # rt
      b |= (self.imm & 0xFFFF) # imm
      return b

    if self.name in j_type.keys():
      b = (j_type[self.name][0]) << 26 #opcode
      b |= (self.imm & 0x03FFFFFF) # address
      return b


  def __repr__(self):
    return "Instruction(%s, %s, %s, %s, %s, %s)"%(self.name, self.rs, self.rt, self.rd, self.imm, self.label)

