.code16 # Instrucciones de 16 bits
	cli  /* Deshabilitamos interrupciones */

	xor %ax, %ax
	mov %ax, %ds /* De osdever. Pone DS en 0. */

	lgdt gdt_desc /* Cargamos la tabla de descriptores. Parentesis? */

	mov %cr0, %eax
	or  $0x1, %eax
	mov %eax, %cr0 /* Seteamos en 1 el bit 0 de cr0 */

	ljmp $0x08, $main

.code32

main:
	mov $0x10, %ax
	mov %ax, %ds
	mov %ax, %ss

	mov $0x090000, %esp  /*osdever*/

hang:
	jmp hang

gdt:

gdt_null:
	.long 0x0 /* Con o sin $? */
	.long 0x0

gdt_code:
        .word 0x0FFFF
        .word 0x0
        .byte 0x0
        .byte 0b10010010
        .byte 0b11001111
        .byte 0x0

gdt_data:               /* Data segment, read/write, expand down */
        .word 0x0FFFF
        .word 0x0
        .byte 0x0
        .byte 0b10010010
        .byte 0b11001111
        .byte 0x0

gdt_end:

gdt_desc:
	.word gdt_end - gdt - 1
	.long gdt
