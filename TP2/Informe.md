# Informe TP2: Sistemas de Computación
## Interacción Python, C y Ensamblador para Procesamiento de Índice GINI

**Grupo:** Grupo1

**Integrantes:**
*   Vasquez Francisco Javier - 43812221 - javier.vasquez@mi.unc.edu.ar


**Fecha de entrega:** 21/04/2025

---

## 1. Introducción

El presente trabajo práctico (TP2) para la asignatura Sistemas de Computación tiene como objetivo principal diseñar e implementar un sistema multicapa que demuestre la interacción entre lenguajes de alto nivel (Python y C) y bajo nivel (Ensamblador x86). El sistema recupera el índice GINI de Argentina desde una API REST pública (Banco Mundial), procesa este dato utilizando una rutina en ensamblador invocada desde C, y presenta el resultado final.

Un aspecto fundamental del trabajo es la aplicación y análisis de las convenciones de llamada (`calling conventions`), específicamente `cdecl` en 32 bits, para gestionar el paso de parámetros (un valor flotante) y la devolución de resultados (un valor entero) entre C y Ensamblador a través de la pila del sistema.

Para validar y comprender en profundidad esta interacción a bajo nivel, se utiliza el depurador GDB, analizando el estado de los registros y la memoria (particularmente la pila) en puntos clave de la ejecución: antes de la llamada a la rutina ensamblador, al inicio de su ejecución, y después de su retorno a C.

Las tecnologías y herramientas empleadas incluyen:
*   Python 3 (con `requests` para la API y `msl-loadlib` o `ctypes` para interactuar con C)
*   Lenguaje C (GCC con flags `-m32` y `-g`)
*   Lenguaje Ensamblador (NASM con flags `-f elf`, `-g`, `-F dwarf`)
*   GNU Debugger (GDB)
*   GNU Make para la automatización del proceso de compilación y depuración.

---

## 2. Arquitectura del Proyecto

El sistema se organiza en las siguientes capas y componentes, siguiendo una estructura modular:



```
TP2 (Raíz)/
|-- Informe.md               
|-- Makefile                   
|-- Readme.md  
python/
|-- main.py                   
|-- main32.py                  
|-- server32_bridge.py       
c/
|-- debug_main.c          
|-- gini_processor.c         
|-- gini_processor.h   
asm/       
|-- gini_calculator.asm    
img/   
```

### Descripción de los Directorios y Archivos

1. **Raíz del Proyecto:**
    - Contiene archivos generales como `Makefile` para la automatización y `Readme.md` para la documentación.

2. **Directorio `python/`:**
    - Scripts en Python que actúan como la capa de más alto nivel, encargados de interactuar con la API REST y la capa C.
    - `main.py`: Versión para sistemas de 64 bits.
    - `main32.py`: Versión para sistemas de 32 bits.
    - `server32_bridge.py`: Bridge para conectar Python 64 bits con la librería compartida C de 32 bits.

3. **Directorio `c/`:**
    - Contiene el código fuente en C que sirve como intermediario entre Python y Ensamblador.
    - `debug_main.c`: Programa independiente para depuración de la interacción C-ASM.
    - `gini_processor.c`: Implementación de la función `process_gini_c` que llama a la rutina ASM.
    - `gini_processor.h`: Archivo de cabecera que declara las funciones de `gini_processor.c`.

4. **Directorio `asm/`:**
    - Contiene el código ensamblador que realiza el cálculo principal.
    - `gini_calculator.asm`: Implementa la rutina `_process_gini_asm` que sigue la convención de llamada `cdecl`.




**Flujo de Datos Principal:**

1.  **Python (`main.py` o `main32.py`):**
    *   Utiliza la librería `requests` para consultar la API del Banco Mundial y obtener el último valor del índice GINI para Argentina.
    *   Prepara la llamada a la capa inferior (C).
        *   `main.py` (64 bits): Actúa como cliente `msl-loadlib`, enviando el valor GINI (float) al `server32_bridge.py`.
        *   `main32.py` (32 bits): Utiliza `ctypes` para cargar directamente la librería compartida C (`libgini_processor.so`) y llamar a `process_gini_c`.
2.  **Bridge/Carga (si aplica):**
    *   `server32_bridge.py`: Recibe la petición del cliente 64b, carga la `libgini_processor.so` (32 bits) y llama a la función `process_gini_c`.
3.  **Capa C (`gini_processor.c`):**
    *   La función `process_gini_c(float gini_value)` actúa como *wrapper*.
    *   Declara la función ensamblador como `extern int _process_gini_asm(float value);`.
    *   Llama a la función `_process_gini_asm`, pasando el `gini_value` (float). El compilador C (GCC) se encarga de generar el código que coloca el parámetro en la pila según la convención `cdecl`.
    *   Recibe el resultado entero devuelto por ASM (en el registro `EAX`) y lo retorna a la capa superior (Python).
4.  **Capa Ensamblador (`gini_calculator.asm`):**
    *   La rutina `_process_gini_asm` (etiqueta global) implementa la convención `cdecl`.
    *   **Prólogo:** Guarda `EBP`, establece el nuevo `EBP`.
    *   **Acceso a Parámetros:** Accede al valor GINI (float) desde la pila en la dirección `[ebp+8]`.
    *   **Procesamiento:**
        *   Carga el float en la FPU (`fld dword [ebp+8]`).
        *   Convierte el float a entero usando `fistp dword [esp]` (guardando temporalmente en pila).
        *   Mueve el resultado entero a `EAX` (`mov eax, [esp]`).
        *   Suma 1 al valor en `EAX` (`add eax, 1`).
    *   **Epílogo:** Restaura `ESP` y `EBP`, retorna a C (`ret`). El resultado final queda en `EAX`.
5.  **Retorno a Python:** El resultado entero viaja de vuelta a través de C y el bridge (si se usó) hasta el script Python original, donde se imprime.

**Componente de Depuración (`debug_main.c`):**

*   Este programa C simple llama directamente a `_process_gini_asm` con un valor flotante fijo (`42.75f`).
*   No interactúa con Python ni la API. Su único propósito es facilitar la depuración detallada de la interfaz C-ASM con GDB, aislando esta interacción específica.

---

## 3. Proceso de Compilación y Depuración (`Makefile`)

El archivo `Makefile` proporcionado automatiza las tareas de compilación y el inicio de la sesión de depuración:

*   **Compilación:**
    *   Ensambla `gini_calculator.asm` a un objeto 32 bits (`obj/gini_calculator.o`) con información de depuración (`-g -F dwarf`).
    *   Compila `gini_processor.c` a un objeto 32 bits (`obj/gini_processor.o`) como código posicionable independiente (`-fPIC`) y con depuración (`-g`).
    *   Enlaza los objetos C y ASM para crear la librería compartida `lib/libgini_processor.so` (32 bits, compartida).
    *   Compila `debug_main.c` y lo enlaza con `obj/gini_calculator.o` para crear el ejecutable de depuración `bin/debug_app` (32 bits, con depuración).
*   **Depuración (`make debug`):**
    *   Genera automáticamente el script `gdb_init_commands.txt`. Este script configura GDB (sintaxis Intel), establece 3 breakpoints estratégicos (antes de la llamada ASM en C, al inicio de la función ASM, después del retorno en C), muestra los breakpoints y presenta mensajes informativos al usuario.
    *   Inicia GDB cargando `bin/debug_app` y ejecutando los comandos desde `gdb_init_commands.txt` (`gdb -q -x gdb_init_commands.txt bin/debug_app`).

---

## 4. Análisis de Depuración con GDB (Interfaz C-ASM)

Utilizando el target `make debug` y el ejecutable `bin/debug_app`, se realizó una sesión de depuración con GDB para analizar en detalle la llamada de la función C `main` (en `debug_main.c`) a la función ensamblador `_process_gini_asm`.

**Objetivo:** Verificar el cumplimiento de la convención `cdecl` (paso de parámetros float por pila, retorno de int en EAX) y observar el estado de la pila y registros clave.

**Paso 1: Inicio y Configuración de GDB**

Se ejecuta `make debug`. GDB inicia, carga el script `gdb_init_commands.txt`, establece los breakpoints y muestra la configuración inicial.

![Configuración Inicial de GDB](/TP2/img/Imagen%20pegada.png)
*Figura 1: Salida inicial de `make debug`, mostrando la carga del script GDB y la configuración de los 3 breakpoints en `c/debug_main.c:29`, `asm/gini_calculator.asm:22` y `c/debug_main.c:33`.*

**Paso 2: Ejecución hasta Breakpoint 1 (Antes de la llamada ASM)**

Se ejecuta el comando `run` en GDB. El programa C se ejecuta hasta la línea 29 de `debug_main.c`, justo antes de invocar `_process_gini_asm`.

![Estado Antes de la Llamada ASM](/TP2/img/Imagen%20pegada%20(2).png)
*Figura 2: GDB detenido en `c/debug_main.c:29`. Se observa el estado de la pila (`$esp = 0xffffcec0`) y el puntero base (`$ebp = 0xffffced8`) correspondientes al stack frame de `main`, *antes* de que se preparen los argumentos para la llamada a `_process_gini_asm`.*

**Paso 3: Ejecución hasta Breakpoint 2 (Dentro de la función ASM)**

Se ejecuta el comando `continue`. GDB ejecuta la llamada (`call`), el prólogo de `_process_gini_asm`, y se detiene en la línea 22 de `asm/gini_calculator.asm`, justo antes de la instrucción `fld`.

![Estado Dentro de la Función ASM](/TP2/img/Imagen%20pegada%20(3).png)
*Figura 3: GDB detenido en `asm/gini_calculator.asm:22`. El análisis del stack frame actual es crucial:*
*   `x/8xw $ebp`: Muestra el contenido relativo al nuevo puntero base (`$ebp = 0xffffcea8`).
    *   `0xffffcea8`: Contiene el `EBP` anterior (de `main`, `0xffffced8`), guardado por el prólogo.
    *   `0xffffceac`: Contiene la dirección de retorno a `main` (`0x56556245`, pusheada por `call`).
    *   `0xffffceb0`: Contiene el **parámetro flotante `0x422b0000`**, que corresponde a `42.75f`, ubicado exactamente en `[ebp+8]` según la convención `cdecl`.
*   `p/f *(float*)($ebp+8)`: Confirma que el valor en `[ebp+8]` se interpreta correctamente como `42.75`.
*   `info registers ebp esp`: Muestra los nuevos punteros de pila y base para el frame de `_process_gini_asm`.
*   `x/10i $pc`: Muestra las siguientes instrucciones ASM, comenzando por `fld dword ptr [ebp+0x8]`.
*   *Esta captura demuestra fehacientemente el paso del parámetro flotante a través de la pila.*

**Paso 4: Ejecución hasta Breakpoint 3 (Después del retorno de ASM)**

Se ejecuta el comando `continue`. La función ASM completa su ejecución (incluyendo `fistp`, `mov eax,...`, `add eax, 1`, epílogo y `ret`), y el control vuelve a `main`. GDB se detiene en la línea 33 de `debug_main.c`, inmediatamente después de la línea donde se realizó la llamada.

![Estado Después del Retorno de ASM](/TP2/img/Imagen%20pegada%20(4).png)
*Figura 4: GDB detenido en `c/debug_main.c:33`. Se observa el estado posterior al retorno:*
*   `info registers eax`: Muestra el **valor de retorno en `EAX`: `0x2c` (44 decimal)**. Este es el resultado calculado por la rutina ASM y devuelto según `cdecl`.
*   `x/16xw $esp`: Muestra el contenido de la pila. El puntero de pila (`$esp = 0xffffcec0`) ha regresado a su valor original (comparar con Figura 2), indicando que la dirección de retorno fue consumida por `ret` y el espacio del parámetro fue limpiado/ignorado por el llamador (C), como dicta `cdecl`.
*   `info registers ebp`: Muestra que el puntero base (`$ebp = 0xffffced8`) ha sido restaurado correctamente al valor de `main` (comparar con Figura 2) gracias al `pop ebp` del epílogo ASM.
*   *Esta captura confirma el correcto retorno del valor en EAX y la restauración del estado del stack frame del llamador.*

**Paso 5: Finalización de la Ejecución**

Se ejecuta el comando `continue` una última vez. El programa C imprime el resultado recibido de ASM y termina normalmente. Se ejecuta `quit` para salir de GDB.

![Finalización del Programa](/TP2/img/Imagen%20pegada%20(5).png)
*Figura 5: El programa C imprime "Resultado recibido de ASM: 44", confirmando que utilizó el valor devuelto en EAX. GDB indica que el programa terminó normalmente (`exited normally`).*

**Discusión del Resultado (44 vs. 43):**

Se observó que el resultado devuelto fue 44 (0x2c), mientras que un truncamiento estricto de 42.75 (dando 42) seguido de la suma de 1 debería dar 43. La investigación sugiere que esto se debe al **modo de redondeo por defecto de la FPU**. La instrucción `fistp` respeta el modo de redondeo configurado en el FPU Control Word. Si el modo es "Redondear al más cercano" (un valor por defecto común), 42.75 se redondea a 43 *antes* de la conversión a entero. Al sumar 1, el resultado final es 44.

La depuración confirma que:
1.  El parámetro float se pasó correctamente en la pila (`[ebp+8]`).
2.  La función ASM accedió a él, realizó operaciones (incluida la conversión FPU->entero).
3.  El resultado entero se devolvió correctamente en el registro `EAX`.
4.  El stack frame del llamador (pila `ESP` y base `EBP`) se restauró adecuadamente.

---

## 5. Conclusión

El Trabajo Práctico 2 se completó exitosamente, desarrollando un sistema funcional que integra Python, C y Ensamblador x86 para obtener y procesar datos del índice GINI. Se implementó la comunicación entre C y Ensamblador utilizando la convención de llamada `cdecl` de 32 bits, gestionando el paso de un parámetro flotante y el retorno de un resultado entero a través de la pila y el registro EAX, respectivamente.

El análisis detallado con GDB, facilitado por un `Makefile` y un programa de depuración dedicado, permitió verificar paso a paso el correcto funcionamiento de esta interfaz de bajo nivel. Las capturas de pantalla documentan el estado de la pila y los registros en puntos críticos, confirmando el apilado del parámetro, el establecimiento del nuevo stack frame en ASM, el acceso al parámetro en `[ebp+8]`, la devolución del resultado en `EAX` y la restauración del contexto del llamador.

La observación del resultado numérico (44 en lugar de 43) condujo a una comprensión más profunda del funcionamiento de la FPU y su dependencia del modo de redondeo, enriqueciendo el aprendizaje sobre la ejecución a bajo nivel.

En resumen, se cumplieron todos los objetivos de la consigna, demostrando la capacidad de interactuar entre diferentes niveles de abstracción de software y validar dicha interacción mediante herramientas de depuración.

---