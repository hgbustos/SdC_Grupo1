; Archivo: TP2/asm/gini_calculator.asm
; Autor: Grupo1
; Descripción: Rutina en ensamblador (NASM) para procesar el índice GINI.
;              Sigue la convención de llamada cdecl (32 bits).
;              - Recibe: un float (32 bits) en la pila ([ebp+8]).
;              - Proceso: Convierte el float a entero (truncando) usando FPU,
;                         luego suma 1 al resultado entero.
;              - Devuelve: un int (32 bits) en el registro EAX.
; Compilación: nasm -f elf -g -F dwarf TP2/asm/gini_calculator.asm -o TP2/obj/gini_calculator.o

section .data
    ; No se necesitan datos inicializados en este ejemplo

section .bss
    ; No se necesita espacio no inicializado en este ejemplo

section .text
    global _process_gini_asm ; Exportar símbolo para que sea visible desde C

_process_gini_asm:
    ; --- Prólogo estándar cdecl ---
    push ebp          ; Guardar el puntero base anterior
    mov ebp, esp      ; Establecer el nuevo puntero base

    ; --- Acceso al parámetro (float) ---
    ; La pila ahora luce así (direcciones bajas arriba):
    ; esp -> [ebp]       <- valor anterior de ebp
    ;        [ebp+4]    <- dirección de retorno (pusheada por CALL)
    ;        [ebp+8]    <- parámetro float gini_value (primer argumento)

    ; --- Procesamiento con FPU ---
    ; Cargar el valor flotante (DWORD = 32 bits) desde la pila [ebp+8] 
    ; a la cima del stack FPU (ST0)
    fld dword [ebp + 8]   

    ; Reservar espacio temporal en la pila para el resultado entero (DWORD = 4 bytes)
    sub esp, 4        
                      
    ; Convertir el float en ST0 a entero (32 bits) y guardarlo en la pila ([esp])
    ; FISTP: Integer Store and Pop. Usa el modo de redondeo actual (normalmente truncar hacia cero).
    ;        Guarda el entero en memoria y hace pop del stack FPU.
    fistp dword [esp] 
    
    ; Recuperar el entero convertido desde la pila al registro EAX (registro de retorno para int)
    mov eax, [esp]    
    
    ; Liberar el espacio temporal reservado en la pila (restaurar esp)
    add esp, 4        

    ; --- Cálculo final ---
    ; Sumar 1 al resultado entero en EAX
    add eax, 1        

    ; --- Epílogo estándar cdecl ---
    mov esp, ebp      ; Restaurar puntero de pila (descarta locales si las hubiera)
    pop ebp           ; Restaurar puntero base anterior
    ret               ; Retornar al llamador (C). Resultado en EAX.

    section .note.GNU-stack noexec    ; Marcar la pila como no ejecutable (buena práctica)