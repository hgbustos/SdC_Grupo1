	.code16 ; Instrucciones de 16 bits
	cli ; Deshabilitamos interrupciones

	xor ax, ax
	mov ds, ax ; De osdever. Pone DS en 0.

	lgdt [gdt_desc] ; Cargamos la tabla de descriptores

	mov eax, cr0
	or eax, 1
	mov cr0, eax ; Seteamos en 1 el bit 0 de cr0

	jmp 08h:main

	.code32
main:
	mov ax, 10h
	mov ds, ax
	mov ss, ax

	mov esp, 090000h ;No entiendo bien esto

hang:
	jmp hang

gdt:

gdt_null:
	dd 0
	dd 0

gdt_code:
        dw 0FFFFh
        dw 0
        db 0
        db 10010010b
        db 11001111b
        db 0

gdt_data:               ; Data segment, read only, expand down
        dw 0FFFFh
        dw 0
        db 0
        db 10010000b ; Write access disabled
        db 11001111b
        db 0

gdt_end:

gdt_desc:
	dw gdt_end - gdt - 1
	dd gdt

times 510-($-$$) db 0 ;Llena el archivo con ceros.
	dw 0AA55h ; Identificador del sector de inicio
