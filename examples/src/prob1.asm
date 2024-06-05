max_number:
  .word 999

i:
  .word 1

a:
  .word 0

number_three:
  .word 3

number_five:
  .word 5

out_addr:
  .word 3

_start:
   loop:
    mov r0, i
    mov r1, a
    mov r2, number_three
    sub r0, r2
    jng increment
    mov r0, i
    mod r0, r2
    jnz next_check
    mov r0, i
    add r1, r0
    jmp increment

   next_check:
    mov r0, i
    mov r2, number_five
    sub r0, r2
    jng increment
    mov r0, i
    mod r0, r2
    jnz increment
    mov r0, i
    add r1, r0

  increment:
   mov r0, i
   mov r2, max_number
   sub r2, r0
   jz output
   inc r0
   mov i, r0
   mov a, r1
   jmp loop

  output:
   mov (out_addr), r1
   hlt