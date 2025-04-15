#ifndef GINI_PROCESSOR_H
#define GINI_PROCESSOR_H

/**
 * @brief Procesa un valor GINI llamando a una rutina en ensamblador.
 * 
 * Esta función actúa como un wrapper. Recibe un valor GINI como flotante, 
 * lo pasa a una rutina en ensamblador (_process_gini_asm) que lo 
 * convierte a entero (truncando), le suma 1 y devuelve el resultado.
 * La comunicación con ensamblador se realiza mediante la pila (convención cdecl).
 *
 * @param gini_value El índice GINI (float) a procesar.
 * @return int El valor entero resultante de la operación en ensamblador 
 *             ( (int)gini_value + 1 ).
 */
int process_gini_c(float gini_value);

#endif // GINI_PROCESSOR_H