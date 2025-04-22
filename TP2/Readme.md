# TP2 - Sistemas de Computación: API REST, Python, C y Ensamblador

## Integrantes

 [Vasquez Francisco Javier](mailto:javier.vasquez@mi.unc.edu.ar)


## Descripción del Proyecto

Este proyecto corresponde al Trabajo Práctico N°2 de la materia Sistemas de Computación. El objetivo es implementar un sistema multicapa que:

1.  Obtiene el índice GINI de Argentina desde una API REST pública (Banco Mundial) utilizando Python (64 bits).
2.  Pasa el valor GINI (float) obtenido a una capa intermedia implementada en C (compilada a 32 bits).
3.  La capa C invoca una rutina escrita en lenguaje Ensamblador (NASM, 32 bits).
4.  La rutina en Ensamblador convierte el valor float a entero (utilizando el redondeo por defecto de FPU, p.ej. 40.7 -> 41), le suma 1 (resultado: 42), y devuelve el resultado entero.
5.  La comunicación entre C y Ensamblador se realiza utilizando la pila, siguiendo la convención de llamada `cdecl` de 32 bits.
6.  El resultado final es devuelto a las capas superiores (C y luego Python) para ser mostrado.

Se utiliza la librería `msl-loadlib` en Python para permitir la interacción entre el intérprete Python principal (64 bits) y la biblioteca C/Ensamblador compilada para 32 bits. Esto se logra mediante un modelo Cliente (64 bits) / Servidor (32 bits).

**Importante:** Un requisito clave del TP es demostrar el funcionamiento de la llamada C -> Ensamblador y el manejo de la pila utilizando el depurador GDB sobre un ejecutable de prueba C puro.

## Prerrequisitos e Instalación

Asegúrate de tener instalado lo siguiente en un sistema **Linux** (probado en Ubuntu 22.04/23.10+ LTS 64 bits):

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

3.  **Python 3 (64 bits), Pip y Venv:**
    *   Pip es el gestor de paquetes de Python.
    *   Venv es necesario para crear entornos virtuales (altamente recomendado).
    ```bash
    # Asegúrate que la versión de python3-venv coincida con tu python3 principal
    sudo apt install python3 python3-pip python3-venv 
    ```
    *(Si usas una versión específica como python3.12, sería `sudo apt install python3.12-venv`)*.

4.  **Dependencias de 32 bits para el Puente Python (msl-loadlib):**
    *   `msl-loadlib` necesita componentes de 32 bits para ejecutar su servidor y cargar la librería.
    *   **Paso 1: Habilitar arquitectura i386 (si no está habilitada):**
        ```bash
        sudo dpkg --add-architecture i386
        sudo apt update
        ```
    *   **Paso 2: Instalar Python 3 y Librerías de Desarrollo (32 bits):**
        ```bash
        # Intenta instalar la versión genérica primero
        sudo apt install python3:i386 libpython3-dev:i386
        ```

    *   **Paso 3: Instalar Zlib (32 bits) - Dependencia de msl-loadlib:**
        ```bash
        sudo apt install zlib1g:i386
        ```
        *(Necesario para que el ejecutable `server32-linux` de msl-loadlib pueda iniciarse).*


5.  **Configurar Entorno Virtual Python:**
    *   **Crear y Activar Entorno Virtual (Recomendado):**
        ```bash
        # Desde la raíz del proyecto clonado (TuRepositorio/)
        python3 -m venv venv
        source venv/bin/activate
        # Para desactivar cuando termines: deactivate
        ```
        *(Asegúrate de reactivar el entorno (`source venv/bin/activate`) cada vez que abras una nueva terminal para trabajar en el proyecto).*

        ## Estructura del Proyecto

        ```plaintext
        TP2 (Raíz)/
        ├── .gitignore               
        ├── Makefile                  
        ├── README.md                 
        ├── asm/
        │   └── gini_calculator.asm   
        ├── c/
        │   ├── debug_main.c          
        │   ├── gini_processor.c      
        │   └── gini_processor.h      
        └── python/
            ├── main.py               
            ├── main32.py             
            └── server32_bridge.py    
## Cómo Compilar y Ejecutar

*   **¡IMPORTANTE! Asegúrate de tener el entorno virtual Python activado (`source venv/bin/activate`) antes de ejecutar los comandos `make run` o `python ...`.**

1.  **Compilar Todo:** Compila la librería C/ASM de 32 bits (`lib/libgini_processor.so`) y el ejecutable C de depuración de 32 bits (`bin/debug_app`).
    ```bash
    make all
    ```

2.  **Ejecutar Flujo Completo (Python 64b -> 32b -> C -> ASM):**
    ```bash
    make run
    ```
    *   **¡Requiere que Python 3 (32 bits), `libpython3-dev:i386` y `zlib1g:i386` estén instalados!** (Ver Prerrequisitos).
    *   Este comando ejecuta `python/main.py` (el cliente 64 bits). Obtendrá el GINI de la API, lo pasará a la librería `.so` a través del puente `msl-loadlib` (que lanza `server32_bridge.py`), y mostrará el resultado final (GINI redondeado + 1).
    *   Si falla, revisa los mensajes de error (especialmente los de `[Client64]` y `[Server32]`) y la sección de Troubleshooting.

3.  **Ejecutar Programa de Depuración C Puro (32 bits):**
    ```bash
    ./bin/debug_app
    ```
    *   Este comando ejecuta directamente el programa C que llama a la función ASM, sin pasar por Python. Ambos (`debug_app` y la rutina ASM) son de 32 bits, por lo que **debería funcionar** incluso si `make run` falla por problemas con el puente Python 64/32 bits.
    *   Salida esperada: `Resultado recibido de ASM: 43` (para el valor de prueba 42.75f, ya que 42.75 se redondea a 43 y se le suma 1). *Corrección: Mi análisis anterior era incorrecto, 42.75 se redondea a 43 con FPU.*

4.  **Iniciar Depuración con GDB (32 bits):**
    ```bash
    make debug
    ```
    *   Inicia GDB cargando el ejecutable `bin/debug_app`. Consulta la sección "Depuración con GDB" a continuación.

5.  **Ejecutar Script Python 32 bits Directo (Opcional / Test Alternativo):**
    *   Este script (`python/main32.py`) intenta cargar la librería `.so` directamente usando `ctypes`. **Requiere ejecutarlo con un intérprete Python 3 de 32 bits.**
    ```bash
    # Necesitas la ruta al ejecutable Python de 32 bits
    /ruta/a/tu/python3_32bit python/main32.py
    ```
    *   Es útil para verificar que la librería `.so` funciona con `ctypes` en un entorno puramente 32 bits, aislando problemas de `msl-loadlib`.

6.  **Limpiar Archivos Generados:** Elimina los directorios `obj/`, `lib/` y `bin/`.
    ```bash
    make clean
    ```

## Depuración con GDB (¡Obligatorio para el TP!)

El objetivo es usar GDB con `bin/debug_app` para verificar la convención de llamada `cdecl` y el paso de parámetros/retorno por la pila y registros entre C y Ensamblador.

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
    *   `layout split` (o `layout reg`, `layout asm`): Muestra registros, código fuente/ASM. Muy útil. Presiona `Ctrl+L` para refrescar la pantalla si se desordena.
    *   `ni` (next instruction): Ejecuta la siguiente instrucción ASM (salta sobre `call`).
    *   `si` (step instruction): Ejecuta la siguiente instrucción ASM (entra en `call`).

4.  **Inspeccionar Registros y Memoria (Pila):**
    *   `info registers eax ebp esp`: Muestra los registros clave. `eax` para el retorno, `ebp`/`esp` para la pila.
    *   `x/16xw $esp`: Examina 16 "words" (4 bytes cada una, en hexadecimal) desde la dirección actual del puntero de pila (`esp`). Útil para ver qué hay *antes* de establecer el frame de la función ASM.
    *   `x/8xw $ebp`: Examina 8 "words" desde el puntero base (`ebp`). Esto es útil *dentro* de la función ASM (después de `mov ebp, esp`) para ver:
        *   `[ebp]` -> Valor de EBP del llamador (guardado por `push ebp`).
        *   `[ebp+4]` -> Dirección de retorno a `debug_main.c` (guardada por `call`).
        *   `[ebp+8]` -> **El parámetro float `test_value`** (primer argumento pasado por C). Debería ser `0x422b0000` para 42.75f.
        *   `[ebp-X]` -> Variables locales de ASM (si las hubiera, como el espacio reservado con `sub esp, 4`).

5.  **¿Qué Observar?**
    *   **Antes de la llamada (en C):** Observa `esp`.
    *   **Dentro de `_process_gini_asm` (después del prólogo `mov ebp, esp`):** Verifica los valores en `[ebp]`, `[ebp+4]`, y especialmente `[ebp+8]` para confirmar que el parámetro float llegó correctamente por la pila.
    *   **Antes del `ret` en ASM:** Verifica que `EAX` contenga el resultado esperado (43).
    *   **Después de volver a C (antes del `printf`):** Verifica que `EAX` todavía contenga 43 (el valor retornado) y que `ESP` y `EBP` se hayan restaurado a los valores que tenían antes de la llamada (aproximadamente).

## Troubleshooting

*   **Error `FATAL ERROR [Client64]: ... Timeout ... Could not connect ... /msl/loadlib/server32-linux: error while loading shared libraries: XXX.so.Y: cannot open shared object file: No such file or directory` durante `make run`:**
    *   **Causa:** El componente servidor 32 bits de `msl-loadlib` no pudo iniciarse porque le falta una dependencia de 32 bits (como `libz.so.1` o `libpython3.X.so.1`).
    *   **Solución:** Instala la versión `:i386` de la librería faltante. Ej: `sudo apt install zlib1g:i386` o `sudo apt install libpython3.X:i386` (reemplaza X con la versión correcta). Asegúrate también de tener `python3:i386` y `libpython3-dev:i386` instalados.
*   **Problemas al instalar `python3:i386`:** Puede haber conflictos de dependencias complejos. Intenta buscar soluciones específicas para tu distribución y versión de Linux o considera probar en otra máquina/VM si es posible.
*   **Errores de compilación (`make all`):** Asegúrate de tener `build-essential`, `nasm`, `gcc-multilib`, `g++-multilib` instalados.
*   **Otros errores de `msl-loadlib`:** Revisa la salida de `[Client64]` y `[Server32]` para obtener pistas. Puede ser un error en `server32_bridge.py` o un problema al cargar `libgini_processor.so` desde el servidor 32 bits.