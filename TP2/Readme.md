# TP2 - Sistemas de Computación: API REST, Python, C y Ensamblador

## Descripción del Proyecto

Este proyecto corresponde al Trabajo Práctico N°2 de la materia Sistemas de Computación. El objetivo es implementar un sistema multicapa que:

1.  Obtiene el índice GINI de Argentina desde una API REST pública (Banco Mundial) utilizando Python.
2.  Pasa el valor GINI (float) obtenido a una capa intermedia implementada en C.
3.  La capa C invoca una rutina escrita en lenguaje Ensamblador (NASM, 32 bits).
4.  La rutina en Ensamblador convierte el valor float a entero (truncando), le suma 1, y devuelve el resultado entero.
5.  La comunicación entre C y Ensamblador se realiza utilizando la pila, siguiendo la convención de llamada `cdecl` de 32 bits.
6.  El resultado final es devuelto a las capas superiores (C y luego Python) para ser mostrado.

Se utiliza la librería `msl-loadlib` en Python para permitir la interacción entre el intérprete Python (generalmente 64 bits) y la biblioteca C/Ensamblador compilada para 32 bits.

**Importante:** Un requisito clave del TP es demostrar el funcionamiento de la llamada C -> Ensamblador y el manejo de la pila utilizando el depurador GDB sobre un ejecutable de prueba C puro.

## Prerrequisitos e Instalación

Asegúrate de tener instalado lo siguiente en un sistema **Linux** (probado en Ubuntu 22.04 LTS 64 bits):

1.  **Herramientas de Construcción Esenciales:**
    ```bash
    sudo apt update
    sudo apt install build-essential nasm git
    ```
    *(Esto instala `gcc`, `make`, `gdb`, `nasm`, etc.)*

2.  **Librerías de Compilación Multi-Arquitectura (32 bits):**
    ```bash
    sudo apt install gcc-multilib g++-multilib
    ```
    *(Necesarias para compilar código C/C++ para 32 bits con la opción `-m32`)*.

3.  **Python 3 (64 bits) y Pip:**
    ```bash
    sudo apt install python3 python3-pip python3-venv
    ```
    *(La versión de 64 bits es para ejecutar el script principal `main.py`)*.

4.  **Python 3 (¡¡32 bits!!) - CRÍTICO para `make run`:**
    *   `msl-loadlib` necesita un intérprete Python de 32 bits para poder cargar la biblioteca `.so` de 32 bits desde el script Python de 64 bits.
    *   **Paso 1: Habilitar arquitectura i386:**
        ```bash
        sudo dpkg --add-architecture i386
        sudo apt update
        ```
    *   **Paso 2: Intentar instalar Python 3 para i386:**
        ```bash
        # Intenta instalar la versión genérica primero
        sudo apt install python3:i386
        ```
        *   **Nota:** La instalación de `python3:i386` puede fallar debido a conflictos de dependencias en algunas versiones de Ubuntu/Debian. Si falla, lamentablemente la ejecución de `make run` (el flujo Python completo) no será posible en esa máquina sin resolver manualmente las dependencias o usar otra estrategia.
    *   **Paso 3 (Si la instalación funcionó):** Verifica dónde se instaló (p. ej., `/usr/bin/python3.X:i386`) y confirma su arquitectura con `file /ruta/al/python3_32bit`.

5.  **Dependencias de Python (usando Entorno Virtual):**
    *   **Crear y Activar Entorno Virtual (Recomendado):**
        ```bash
        # Desde la raíz del proyecto clonado
        python3 -m venv venv
        source venv/bin/activate
        # Para desactivar: deactivate
        ```
    *   **Instalar Librerías:**
        ```bash
        # Asegúrate de tener un archivo requirements.txt con:
        # requests
        # msl-loadlib
        pip install -r requirements.txt
        ```
        *(Crea un archivo `requirements.txt` en la raíz con las dos líneas anteriores)*

## Estructura del Proyecto

TP2 (Raíz)/
|-- Makefile # Automatiza compilación, ejecución y limpieza
|-- requirements.txt # Dependencias de Python
|-- README.md # Este archivo
|-- generate_summary.py # Script para generar resumen (opcional)
|-- asm/
| |-- gini_calculator.asm # Rutina principal en Ensamblador
|-- python/
| |-- main.py # Script principal: API -> C -> ASM -> Resultado
|-- c/
| |-- debug_main.c # Programa C puro para depurar ASM con GDB
| |-- gini_processor.c # Wrapper C que llama a la función ASM
| |-- gini_processor.h # Header para el wrapper C
|-- obj/ # (Generado) Archivos objeto compilados
|-- lib/ # (Generado) Biblioteca compartida (.so)
|-- bin/ # (Generado) Ejecutable de depuración
|-- venv/ # (Opcional) Directorio del entorno virtual Python


## Cómo Compilar y Ejecutar

*   **Asegúrate de tener el entorno virtual Python activado (`source venv/bin/activate`) si lo usas.**

1.  **Compilar Todo:** Compila la librería C/ASM de 32 bits (`.so`) y el ejecutable C de depuración de 32 bits (`debug_app`).
    ```bash
    make all
    ```

2.  **Ejecutar Flujo Completo (Python -> C -> ASM):**
    ```bash
    make run
    ```
    *   **¡Requiere que Python 3 (32 bits) esté instalado y sea encontrable por `msl-loadlib`!**
    *   Este comando ejecuta `python/main.py`. Obtendrá el GINI de la API, lo pasará a la librería `.so` (usando `msl-loadlib` como puente), y mostrará el resultado final (GINI convertido a entero + 1).
    *   Si obtienes el error `wrong ELF class: ELFCLASS32`, significa que `msl-loadlib` no pudo usar/encontrar el intérprete Python de 32 bits. Revisa la sección de Prerrequisitos.

3.  **Ejecutar Programa de Depuración C Puro:**
    ```bash
    ./bin/debug_app
    ```
    *   Este comando ejecuta directamente el programa C que llama a la función ASM, sin pasar por Python. Ambos (`debug_app` y la rutina ASM) son de 32 bits, por lo que **debería funcionar** incluso si `make run` falla por problemas de `msl-loadlib`.
    *   Salida esperada: `Resultado recibido de ASM: 43` (para el valor de prueba 42.75f).

4.  **Iniciar Depuración con GDB:**
    ```bash
    make debug
    ```
    *   Inicia GDB cargando el ejecutable `bin/debug_app`. Consulta la sección "Depuración con GDB" a continuación.

5.  **Limpiar Archivos Generados:** Elimina los directorios `obj`, `lib` y `bin`.
    ```bash
    make clean
    ```

## Depuración con GDB (¡Obligatorio para el TP!)

El objetivo es usar GDB con `bin/debug_app` para verificar la convención de llamada `cdecl` y el paso de parámetros por la pila entre C y Ensamblador.

1.  **Iniciar GDB:**
    ```bash
    make debug
    ```
    o
    ```bash
    gdb ./bin/debug_app
    ```

2.  **Poner Breakpoints:**
    *   Antes de la llamada a ASM en C: `b debug_main.c:28` (o la línea donde está `result = _process_gini_asm(test_value);`)
    *   Al inicio de la función ASM: `b _process_gini_asm`
    *   *Opcional:* Justo antes del `ret` en ASM (requiere desensamblar: `disass _process_gini_asm`, encontrar la dirección del `ret`, y poner breakpoint ahí: `b *<direccion>`).
    *   Después de volver de ASM en C: `b debug_main.c:33` (o la línea del `printf` del resultado).

3.  **Ejecutar y Avanzar:**
    *   `run`: Inicia la ejecución hasta el primer breakpoint.
    *   `c` o `continue`: Continúa hasta el siguiente breakpoint.
    *   `layout split` (o `layout reg`, `layout asm`): Muestra registros, código fuente/ASM. Muy útil.
    *   `ni` (next instruction): Ejecuta la siguiente instrucción ASM (salta sobre `call`).
    *   `si` (step instruction): Ejecuta la siguiente instrucción ASM (entra en `call`).

4.  **Inspeccionar Registros y Memoria (Pila):**
    *   `info registers eax ebp esp`: Muestra los registros clave.
    *   `x/16xw $esp`: Examina 16 "words" (4 bytes cada una, en hexadecimal) desde la dirección actual del puntero de pila (`esp`).
    *   `x/4xw $ebp`: Examina 4 "words" desde el puntero base (`ebp`). Esto es útil *dentro* de la función ASM para ver:
        *   `[ebp]` -> EBP del llamador (guardado por `push ebp`).
        *   `[ebp+4]` -> Dirección de retorno (guardada por `call`).
        *   `[ebp+8]` -> **El parámetro float `test_value`** (primer argumento pasado por C).

5.  **¿Qué Observar?**
    *   **Antes de la llamada:** ¿Cómo está la pila? (Puede que no veas el parámetro directamente si `gcc` lo optimiza pasándolo por registro FPU antes de la llamada final, pero la dirección de retorno estará después del `call`).
    *   **Dentro de `_process_gini_asm` (después del prólogo):** Verifica que `[ebp]` contenga el EBP anterior, `[ebp+4]` la dirección de retorno a `debug_main.c`, y `[ebp+8]` los 4 bytes correspondientes al float `42.75f` (Hex: `0x422b0000`).
    *   **Antes del `ret`:** Verifica que `EAX` contenga el resultado esperado (43).
    *   **Después de volver a C:** Verifica que `EAX` todavía contenga 43 (ya que `result` se asigna desde `EAX`) y que `ESP` y `EBP` se hayan restaurado correctamente.

## Troubleshooting

*   **Error `wrong ELF class: ELFCLASS32` durante `make run`:**
    *   **Causa:** Python 64 bits no puede cargar la librería `.so` de 32 bits directamente, y `msl-loadlib` no encontró un intérprete Python 3 de 32 bits para crear el puente necesario.
    *   **Solución:** Asegúrate de haber instalado `python3:i386` (ver Prerrequisitos). Si lo instalaste pero sigue fallando, `msl-loadlib` podría no encontrarlo. Puedes indicarle la ruta explícitamente con una variable de entorno:
        ```bash
        export MSL_LOADLIB_PYTHON32_EXE=/ruta/a/tu/python3_32bit
        make run
        ```
        (Reemplaza `/ruta/a/tu/python3_32bit` con la ruta real).
*   **Problemas al instalar `python3:i386`:** Puede haber conflictos de dependencias complejos. Intenta buscar soluciones específicas para tu distribución y versión de Linux o considera probar en otra máquina/VM si es posible.
*   **Errores de compilación (`make all`):** Asegúrate de tener `build-essential`, `nasm`, `gcc-multilib`, `g++-multilib` instalados.

## Autores

    Vasquez Francisco Javier