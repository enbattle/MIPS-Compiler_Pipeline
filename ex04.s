asdf:
addi $t2,$s0,73
ias:
andi $t1,$s0,73
branch:
bne $t1,$t1,loop
beq $t2,$t1,loop
ori $s1,$zero,451
add $t4,$s1,$s7
beq $s1,$t9,loop
loop:
ori $s0,$zero,24
