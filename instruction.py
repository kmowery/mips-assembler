import re

import itertools
from register import Register, UnusedRegister

NAME_NO_SPACE = "(?P<name>[a-zA-Z]+)"
NAME   = NAME_NO_SPACE + "\s+"
LABEL  = "(?P<label>[a-zA-Z_][_0-9a-zA-Z]+)\s*"
IMM    = "(?P<imm>-?[0-9][x0-9A-Fa-f]*)\s*"
FIRST  = "(?P<first>\$[0-9a-zA-Z]+)\s*"
SECOND = "(?P<second>\$[0-9a-zA-Z]+)\s*"
THIRD  = "(?P<third>\$[0-9a-zA-Z]+)\s*"
COMMA  = "\s*,\s*"
EOL    = "\s*(#.*)?$"

LINE_BEGIN = r"(?i)^[^#]*?"

instruction_types = [
    re.compile(LINE_BEGIN +
      NAME + FIRST + COMMA + SECOND + COMMA + THIRD + EOL),

    re.compile(LINE_BEGIN +
      NAME + FIRST + COMMA + SECOND + COMMA + LABEL + EOL),

    re.compile(LINE_BEGIN +
      NAME + FIRST + COMMA + SECOND + COMMA + IMM + EOL),

    re.compile(LINE_BEGIN +
      NAME + FIRST + COMMA + IMM + "\(\s*" + SECOND + "\s*\)\s*" + EOL),

    re.compile(LINE_BEGIN +
      NAME + FIRST + COMMA + LABEL + EOL),

    re.compile(LINE_BEGIN +
      NAME + FIRST + COMMA + IMM + EOL),

    re.compile(LINE_BEGIN +
      NAME + FIRST + EOL),

    re.compile(LINE_BEGIN +
      NAME + LABEL + EOL),

    re.compile(LINE_BEGIN +
      NAME + IMM + EOL),

    re.compile(LINE_BEGIN +
      NAME_NO_SPACE + EOL)
]

r_type = {
  "add":     (0x0,0b100000, ["rd", "rs", "rt"]),
  "addu":    (0x0,0b100001, ["rd", "rs", "rt"]),
  "and":     (0x0,0b100100, ["rd", "rs", "rt"]),
  "break":   (0x0,0b001101, []),
  "div":     (0x0,0b011010, ["rd", "rs", "rt"]),
  "divu":    (0x0,0b011011, ["rs", "rt"]),
  "jalr":    (0x0,0b001001, ["rd", "rs"]),
  "jr":      (0x0,0b001000, ["rs"]),
  "mfhi":    (0x0,0b010000, ["rd"]),
  "mflo":    (0x0,0b010010, ["rd"]),
  "mthi":    (0x0,0b010001, ["rs"]),
  "mtlo":    (0x0,0b010011, ["rs"]),
  "mult":    (0x0,0b011000, ["rs", "rt"]),
  "multu":   (0x0,0b011001, ["rs", "rt"]),
  "nor":     (0x0,0b100111, ["rd", "rs", "rt"]),
  "or":      (0x0,0b100101, ["rd", "rs", "rt"]),
  "sll":     (0x0,0b000000, ["rd", "rt"]),
  "sllv":    (0x0,0b000100, ["rd", "rt"]),
  "slt":     (0x0,0b101010, ["rd", "rs", "rt"]),
  "sltu":    (0x0,0b101011, ["rd", "rs", "rt"]),
  "sra":     (0x0,0b000011, ["rd", "rt"]),
  "srav":    (0x0,0b000111, ["rd", "rt"]),
  "srl":     (0x0,0b000010, ["rd", "rt"]),
  "srlv":    (0x0,0b000110, ["rd", "rt", "rs"]),
  "sub":     (0x0,0b100010, ["rd", "rs", "rt"]),
  "subu":    (0x0,0b100011, ["rd", "rs", "rt"]),
  "syscall": (0x0,0b001100, []),
  "xor":     (0x0,0b100110, ["rd", "rs", "rt"]),
}

i_type = {
  "addi":  (0b001000,["rt", "rs"]),
  "addiu": (0b001001,["rt", "rs"]),
  "andi":  (0b001100,["rt", "rs"]),
  "beq":   (0b000100,["rs", "rt"]),
  "bgez":  (0b000001,0b00001,["rs"]),
  "bgtz":  (0b000111,0b00000,["rs"]),
  "blez":  (0b000110,0b00000,["rs"]),
  "bltz":  (0b000001,0b00000,["rs"]),
  "bne":   (0b000101,["rs", "rt"]),
  "lb":    (0b100000,["rt", "rs"]),
  "lbu":   (0b100100,["rt", "rs"]),
  "lh":    (0b100001,["rt", "rs"]),
  "lhu":   (0b100101,["rt", "rs"]),
  "lui":   (0b001111,["rt"]),
  "lw":    (0b100011,["rt", "rs"]),
  "lwc1":  (0b110001,["rt", "rs"]),
  "ori":   (0b001101,["rt", "rs"]),
  "sb":    (0b101000,["rt", "rs"]),
  "slti":  (0b001010,["rt", "rs"]),
  "sltiu": (0b001011,["rt", "rs"]),
  "sh":    (0b101001,["rt", "rs"]),
  "sw":    (0b101011,["rt", "rs"]),
  "sc":    (0b111000,["rt", "rs"]),
  "swc1":  (0b111001,["rt", "rs"]),
  "xori":  (0b001110,["rt", "rs"]),
}

j_type = {
"j":       (0b000010,[]),
"jal":     (0b000011,[]),
}

supported_pseudoinstructions = ['li', 'nop']

def MakeInstruction(position, **kwargs):
  if 'name' in kwargs and \
      kwargs['name'].lower() in supported_pseudoinstructions:
    return PsedoInstruction(position, **kwargs)
  else:
    return Instruction(position, **kwargs)

# Sometimes we will consider imm to be shamt.
class Instruction:
  def __init__(self, program, position, name=None,
      first=None, second=None, third=None,
      imm=None, label=None):

    name = name.lower()
    if name not in r_type.keys() and \
       name not in i_type.keys() and \
       name not in j_type.keys():
      raise Exception("'%s' is not a MIPS opcode"%(name.lower()))

    self.program = program
    self.position = position
    self.name = name

    self.rs = UnusedRegister()
    self.rt = UnusedRegister()
    self.rd = UnusedRegister()

    # Verify that the right registers are present
    registers = (r_type[name][-1] if name in r_type else \
                 i_type[name][-1] if name in i_type else \
                 j_type[name][-1])
    rlist = [x for x in [first, second, third] if x is not None]

    if len(registers) == 3 and (first is None or second is None \
        or third is None):
      raise Exception("'%s' requires three registers"%(name))
    if len(registers) == 2 and (first is None or second is None \
        or third is not None):
      raise Exception("'%s' requires two registers"%(name))
    if len(registers) == 1 and (first is None or second is not None \
        or third is not None):
      raise Exception("'%s' requires one register"%(name))
    if len(registers) == 0 and (first is not None or second is not None \
        or third is not None):
      raise Exception("'%s' requires no registers"%(name))

    for pos,reg in zip(registers, rlist):
      if pos == "rs": self.rs = Register(reg)
      if pos == "rd": self.rd = Register(reg)
      if pos == "rt": self.rt = Register(reg)

    if isinstance(imm, int):
      self.imm = imm
    else:
      self.imm = eval(imm) if imm is not None else 0
    self.label = label

    if imm is not None and self.label is not None:
      raise Exception("A label and an immediate. Confused.")

  @staticmethod
  def parseline(program, position, line):
    global instruction_types
    for t in instruction_types:
      m = t.match(line)
      if m is not None:
        g = m.groupdict()

        if 'name' in g and \
            g['name'].lower() in supported_pseudoinstructions:
          return PseudoInstruction(program, position, **m.groupdict())

        return Instruction(program=program, position=position, **g)
    raise Exception("'%s' not an instruction"%(line))

  def ToBinary(self):
    if self.name in r_type.keys():
      b = 0                            # opcode
      b |= (self.rs.binary() << 21)    # rs
      b |= (self.rt.binary() << 16)    # rt
      b |= (self.rd.binary() << 11)    # rd

      b |= (self.imm << 6)             # shamt
      b |= (r_type[self.name][1] << 0) # funct
      return b

    if self.name in i_type.keys():
      b = i_type[self.name][0] << 26 # opcode
      b |= (self.rs.binary() << 21)  # rs
      b |= (self.rt.binary() << 16)  # rt
      if len(i_type[self.name]) > 2:
        # this is a b[gl][et]z instruction. Mux this in.
        b |= (i_type[self.name][1] << 16)  # rt adjustment

      if self.label is not None:
        # horribly hacky. are we a branch?
        if "b" == self.name[0]:
          z =  self.program.Label(self.label) - self.position - 1
        else:
          z =  self.program.Label(self.label)
        b |= (z & 0xFFFF)         # label
      else:
        # horribly hacky. are we a branch?
        if "b" == self.name[0]:
          b |= (self.imm>>2 & 0xFFFF) # imm
        else:
          b |= (self.imm & 0xFFFF)   # imm

      return b

    if self.name in j_type.keys():
      b = (j_type[self.name][0]) << 26 #opcode
      if self.label is not None:
        b |= (self.program.Label(self.label) +
            (self.program.text_base >> 2)) # label
      else:
        b |= (self.imm >> 2 & 0x03FFFFFF) # address
      return b

  # The size, in words, of this instruction
  def Size(self):
    return 1

  def Bytes(self, endian="big"):
    b = self.ToBinary()
    bytes = [ b >> 24,
              b >> 16 & 0xFF,
              b >> 8 & 0xFF,
              b & 0xFF ]
    return bytes[::-1] if endian.lower() == "little" else bytes


  def __repr__(self):
    return "Instruction(%s, %s, %s, %s, %s, %s)"% \
       (self.name, self.rs, self.rt, self.rd, self.imm, self.label)


class PseudoInstruction:
  def __init__(self, program, position, name=None,
      first=None, second=None, third=None,
      imm=None, label=None):
    self.name = name.lower()
    self.program = program
    self.position = position
    self.instructions = []

    if name == "li":
      if label is not None:
        # get all fancy
        self.instructions.append(Instruction(self.program, position,
          name="lui", first=first,
          label=lambda: program.Label(label) >> 16 & 0xFFFF))
        self.instructions.append(Instruction(self.program, position+1,
          name="ori", first=first, second=first,
          label=lambda: program.Label(label) & 0xFFFF))
      else:
        self.instructions.append(Instruction(self.program, position,
          name="lui", first=first,
          imm=((eval(imm) >> 16) & 0xFFFF)))
        self.instructions.append(Instruction(self.program, position+1,
          name="ori", first=first, second=first,
          imm=(eval(imm) & 0xFFFF)))
    elif name == "nop":
      self.instructions.append(Instruction(self.program, position,
        name="sll", first="$0", second="$0", imm="0x0"))
    else:
      raise "'%s' not support/not a pseudoinstruction"%(name)

  def Bytes(self, endian="big"):
    return list(itertools.chain( *[x.Bytes(endian=endian) for x
      in self.instructions] ))

  def Size(self):
    return sum([x.Size() for x in self.instructions])

  def ToBinary(self):
    x = 0;
    raise Exception("ToBinary called on a PseudoInstruction")

