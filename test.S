.STRING no "012345678"
.STRING printfstr "012345678"

.DEFINE SBIDH_CC_MASK 0xfff0
.DEFINE SBIDH_CC_SHIFT 4

.DEFINE SB_CORE_SIZE 0x1000

main:
jr $ra

  #addiu $a0, $a0, SB_CORE_SIZE
  addiu $t9,$0,0xfff
  srl  $k1, $k1, SBIDH_CC_SHIFT

#  jal 0x38a14
#freeze:
#  beq $0, $0, freeze
#  addi $t0, $t0, freeze
#  addi $t0, $t0, 0x1234
#  nop
#  add $t0, $0, $0
#elsewhere:
#  addi $t0, $t0, 0x20
#  beq $t7, $a3, main
#  beq $t0, $t0, 0x1
#  bne $t0, $t0, nope
#  beq $t0, $t0, 0x16
#  nop
#nope:
#  beq $t0, $t0, main
#  j main
#  jal nope
#  j 0x0010000
#  BGEZ $t5, main
#  bgtz $gp, main
#  bltz $t5, nope
#three:
#  blez $k0, three
#  li $t9, 0x40507098
#  ori $t9, 0x7098
#seriously:
#  nop
#  j seriously
#  add $0, $0, $0
#  addi $t9, $t9, printfstr
#  bgez $t0, nope
#  beq $t0, $0, nope
#  li $t0, 0x45679087
#  li $t0, printfstr
#
#
#  j main
#  jal main
#nope:
#  jr $0
#  lbu $t0, 0x04($0)
#  lui $t0, 0x8403
#  lw $t0, 0x04($0)
#  ori $t4, $sp, 0x4
#  slt $fp, $ra, $t0
#  slti $v0, $v1, 0x5
#  sll $zero, $at, 0x5
#  sb $t0,0x04($s0)
#  sc $t0,0xFF($s0)

