#include <stdio.h>

/**
 * @brief Declaración externa de la función implementada en ensamblador.
 * @see TP2/asm/gini_calculator.asm
 */
extern int _process_gini_asm(float value);

/**
 * @brief Programa principal simple para probar y depurar la llamada C -> ASM.
 * 
 * Este programa no usa la API ni Python, solo llama directamente a la 
 * rutina ensamblador con un valor fijo para facilitar la depuración con GDB.
 * Compilar con: gcc -m32 -g TP2/c/debug_main.c TP2/obj/gini_calculator.o -o TP2/bin/debug_app
 * Ejecutar con GDB: gdb TP2/bin/debug_app
 */
int main() {
    float test_value = 42.75f; // Valor de prueba (float)
    int result;

    printf("--- Inicio del programa de depuración C ---\n");
    printf("Valor de prueba (float): %f (Hex: 0x%x)\n", test_value, *(unsigned int*)&test_value);
    
    // --- Punto de interés 1: Antes de llamar a ASM ---
    printf("[DEBUG] Punto 1: Inmediatamente antes de llamar a _process_gini_asm.\n");
    printf("          Inspeccionar pila (esp) y registros (ebp) aquí.\n");
    // Colocar breakpoint en GDB en la siguiente línea (llamada a ASM)
    
    result = _process_gini_asm(test_value); // Llamada a la función ensamblador
                                            // Colocar breakpoint GDB en _process_gini_asm
    
    // --- Punto de interés 2: Después de volver de ASM ---
    printf("[DEBUG] Punto 2: Inmediatamente después de volver de _process_gini_asm.\n");
    printf("          Inspeccionar resultado en EAX y estado de la pila (esp, ebp).\n");
    // Colocar breakpoint en GDB en la siguiente línea (printf resultado)
    
    printf("Resultado recibido de ASM: %d\n", result);
    
    printf("--- Fin del programa de depuración C ---\n");
    
    return 0;
}