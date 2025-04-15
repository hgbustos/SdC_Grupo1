#include "gini_processor.h"
#include <stdio.h> // Incluido por si se necesitan prints de debug temporalmente

/**
 * @brief Declaración externa de la función implementada en ensamblador.
 * 
 * Se espera que esta función siga la convención de llamada cdecl:
 * - Recibe un float de 32 bits en la pila ([ebp+8]).
 * - Devuelve un int de 32 bits en el registro EAX.
 * - El llamador (esta función C) es responsable de limpiar la pila.
 * El nombre '_process_gini_asm' debe coincidir con la etiqueta 'global' en el archivo .asm.
 */
extern int _process_gini_asm(float value); 

/**
 * @brief Implementación del wrapper C que llama a la función ensamblador.
 * @see gini_processor.h
 */
int process_gini_c(float gini_value) {
    // printf("[C Wrapper] Llamando a ensamblador con valor: %f\n", gini_value); // Descomentar para depurar
    
    // Llamar directamente a la función ensamblador
    int result_from_asm = _process_gini_asm(gini_value); 
    
    // printf("[C Wrapper] Ensamblador devolvió: %d\n", result_from_asm); // Descomentar para depurar
    
    // Devolver el resultado obtenido del ensamblador
    return result_from_asm;
}