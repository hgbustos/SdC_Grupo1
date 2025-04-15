# Resumen del Proyecto TP2

```
TP2 (Raíz)/
  |-- Makefile
  |-- Readme.md
  |-- generate_sumary.py
asm/
  |-- gini_calculator.asm
python/
  |-- main.py
c/
  |-- debug_main.c
  |-- gini_processor.c
  |-- gini_processor.h
```

---

## Contenido de Archivos

### `Makefile`

```makefile
# Makefile para el TP2 de Sistemas de Computación
# Compilación cruzada Python(64) -> C/ASM(32) y Debug App (32)

# --- Herramientas ---
NASM = nasm
CC = gcc
PYTHON = python3

# --- Flags ---
# -f elf: Formato objeto para Linux
# -g -F dwarf: Información de depuración para GDB
ASMFLAGS = -f elf -g -F dwarf
# -m32: Compilar para arquitectura de 32 bits
# -g: Incluir información de depuración
# -Wall: Mostrar todos los warnings
# -c: Compilar a objeto, sin enlazar
# -O0: Deshabilitar optimizaciones (mejor para depurar)
COBJFLAGS = -m32 -g -Wall -c -O0
# -fPIC: Generar código independiente de la posición (necesario para .so)
CFLAGS_SO = $(COBJFLAGS) -fPIC
# -shared: Crear una biblioteca compartida (.so)
LDFLAGS_SO = -m32 -shared -g
# Flags para enlazar el ejecutable de depuración (32 bits, con debug info)
LDFLAGS_EXE = -m32 -g

# --- Directorios ---
SRC_DIR_C = c
SRC_DIR_ASM = asm
SRC_DIR_PY = python
OBJ_DIR = obj
LIB_DIR = lib
BIN_DIR = bin

# --- Archivos Fuente ---
# Excluir debug_main.c de las fuentes para la librería
C_SOURCES_LIB = $(filter-out $(SRC_DIR_C)/debug_main.c, $(wildcard $(SRC_DIR_C)/*.c))
ASM_SOURCES = $(wildcard $(SRC_DIR_ASM)/*.asm)
C_DEBUG_SOURCE = $(SRC_DIR_C)/debug_main.c
PY_MAIN = $(SRC_DIR_PY)/main.py

# --- Archivos Objeto ---
# Objeto para el wrapper C de la librería
C_OBJS_LIB = $(patsubst $(SRC_DIR_C)/%.c, $(OBJ_DIR)/%.o, $(C_SOURCES_LIB))
# Objeto para el código ensamblador
ASM_OBJS = $(patsubst $(SRC_DIR_ASM)/%.asm, $(OBJ_DIR)/%.o, $(ASM_SOURCES))

# --- Archivos de Salida ---
# Biblioteca compartida para Python
LIB_TARGET = $(LIB_DIR)/libgini_processor.so
# Ejecutable independiente para depuración con GDB
DEBUG_TARGET = $(BIN_DIR)/debug_app

# --- Reglas ---

# Regla por defecto: construir la biblioteca compartida Y el ejecutable de debug
all: $(LIB_TARGET) $(DEBUG_TARGET)

# --- Reglas de Construcción de Archivos ---

# Construir la biblioteca compartida (.so)
$(LIB_TARGET): $(C_OBJS_LIB) $(ASM_OBJS)
	@echo "MKDIR (if needed) -> $(LIB_DIR)"
	@mkdir -p $(LIB_DIR)
	@echo "LD (Shared Lib) -> $@"
	$(CC) $(LDFLAGS_SO) -o $@ $^ # $^ incluye todos los .o dependientes

# Construir el ejecutable de depuración (CORREGIDO)
$(DEBUG_TARGET): $(C_DEBUG_SOURCE) $(ASM_OBJS)
	@echo "MKDIR (if needed) -> $(BIN_DIR)"
	@mkdir -p $(BIN_DIR)
	@echo "LD (Debug App) -> $@"
	# Corrección: Usar $@ para el output y $^ para las dependencias (debug_main.c y gini_calculator.o)
	$(CC) $(LDFLAGS_EXE) -o $@ $^

# Compilar objetos C para la biblioteca compartida (con -fPIC)
# Usamos una regla específica para gini_processor.o ya que solo ese va en la .so
$(OBJ_DIR)/gini_processor.o: $(SRC_DIR_C)/gini_processor.c $(SRC_DIR_C)/gini_processor.h
	@echo "MKDIR (if needed) -> $(OBJ_DIR)"
	@mkdir -p $(OBJ_DIR)
	@echo "CC (PIC Object) -> $@"
	$(CC) $(CFLAGS_SO) $< -o $@ # $< es la primera dependencia (gini_processor.c)

# Ensamblar objetos ASM (regla genérica para cualquier .asm)
$(OBJ_DIR)/%.o: $(SRC_DIR_ASM)/%.asm
	@echo "MKDIR (if needed) -> $(OBJ_DIR)"
	@mkdir -p $(OBJ_DIR)
	@echo "ASM -> $@"
	$(NASM) $(ASMFLAGS) $< -o $@

# --- Reglas de Acciones (Phony) ---

run: $(LIB_TARGET)
	@echo "=== Ejecutando Script Python $(PY_MAIN) ==="
	$(PYTHON) $(PY_MAIN)

debug: $(DEBUG_TARGET)
	@echo "=== Iniciando GDB para $(DEBUG_TARGET) ==="
	gdb $(DEBUG_TARGET)

clean:
	@echo "Limpiando directorios: $(OBJ_DIR) $(LIB_DIR) $(BIN_DIR)"
	@rm -rf $(OBJ_DIR) $(LIB_DIR) $(BIN_DIR)
	@echo "Limpieza completada."

# Phony targets: No son archivos, son comandos
.PHONY: all run debug clean
```

---

### `generate_sumary.py`

```python
import os
import fnmatch # Para patrones de archivos/directorios

# --- Configuración ---
OUTPUT_FILENAME = "project_summary.md"
START_DIR = "."  # Directorio actual (asume que se ejecuta desde TP2/)

# Extensiones de archivo cuyo contenido queremos incluir
CONTENT_EXTENSIONS = {".py", ".c", ".h", ".asm"} 
# Archivos específicos (sin extensión o nombre exacto) cuyo contenido incluir
CONTENT_FILENAMES = {"Makefile"}

# Lenguajes para bloques de código Markdown (aproximado)
LANGUAGE_HINTS = {
    ".py": "python",
    ".c": "c",
    ".h": "c",
    ".asm": "assembly",
    "Makefile": "makefile",
}

# Directorios a ignorar completamente
IGNORE_DIRS = {"venv", "__pycache__", ".git", "obj", "lib", "bin"}
# Archivos específicos a ignorar
IGNORE_FILES = {OUTPUT_FILENAME, ".gitignore", "generate_summary.py"} 
# Patrones de archivos a ignorar (usando fnmatch)
IGNORE_PATTERNS = {"*.pyc", "*.o", "*.so", "*.out", "*~", "debug_app"}

# Máxima profundidad de directorios a mostrar (ajustable)
MAX_DEPTH = 5 
# Tamaño máximo de archivo para incluir contenido (en bytes, para evitar archivos enormes)
MAX_FILE_SIZE_CONTENT = 50 * 1024 # 50 KB

# --- Funciones ---

def should_ignore(name, path, is_dir):
    """Verifica si un archivo o directorio debe ser ignorado."""
    base_name = os.path.basename(path)
    if is_dir:
        return base_name in IGNORE_DIRS
    else:
        if base_name in IGNORE_FILES:
            return True
        for pattern in IGNORE_PATTERNS:
            if fnmatch.fnmatch(base_name, pattern):
                return True
        return False

def get_language_hint(filename):
    """Obtiene la pista de lenguaje para Markdown basada en la extensión o nombre."""
    if filename in CONTENT_FILENAMES:
        return LANGUAGE_HINTS.get(filename, "")
    _, ext = os.path.splitext(filename)
    return LANGUAGE_HINTS.get(ext, "")

# --- Script Principal ---

try:
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as md_file:
        md_file.write(f"# Resumen del Proyecto TP2\n\n")
        md_file.write("```\n") # Bloque para la estructura de árbol inicial
        
        tree_structure = []
        for dirpath, dirnames, filenames in os.walk(START_DIR, topdown=True):
            # Ignorar directorios especificados (modifica dirnames in-place)
            dirnames[:] = [d for d in dirnames if not should_ignore(d, os.path.join(dirpath, d), True)]
            
            relative_path = os.path.relpath(dirpath, START_DIR)
            depth = relative_path.count(os.sep) if relative_path != '.' else 0

            if depth > MAX_DEPTH:
                dirnames[:] = [] # No seguir descendiendo
                continue

            indent = "  " * depth
            dir_prefix = "|-- " if depth > 0 else ""
            display_name = os.path.basename(dirpath) if relative_path != '.' else "TP2 (Raíz)"
            tree_structure.append(f"{indent}{dir_prefix}{display_name}/")

            # Ignorar archivos especificados
            valid_files = sorted([f for f in filenames if not should_ignore(f, os.path.join(dirpath, f), False)])
            
            file_indent = "  " * (depth + 1)
            for filename in valid_files:
                 tree_structure.append(f"{file_indent}|-- {filename}")

        md_file.write("\n".join(tree_structure))
        md_file.write("\n```\n\n") # Fin del bloque de árbol

        md_file.write("---\n\n")
        md_file.write("## Contenido de Archivos\n\n")

        # Segunda pasada para escribir contenido
        for dirpath, dirnames, filenames in os.walk(START_DIR, topdown=True):
            # Ignorar directorios (de nuevo)
            dirnames[:] = [d for d in dirnames if not should_ignore(d, os.path.join(dirpath, d), True)]

            relative_path = os.path.relpath(dirpath, START_DIR)
            depth = relative_path.count(os.sep) if relative_path != '.' else 0
            
            if depth > MAX_DEPTH:
                 dirnames[:] = []
                 continue

            # Ignorar archivos
            valid_files = sorted([f for f in filenames if not should_ignore(f, os.path.join(dirpath, f), False)])

            for filename in valid_files:
                file_path = os.path.join(dirpath, filename)
                _, ext = os.path.splitext(filename)
                
                # Comprobar si debemos incluir el contenido
                include_content = (ext in CONTENT_EXTENSIONS or filename in CONTENT_FILENAMES)
                
                if include_content:
                    relative_file_path = os.path.relpath(file_path, START_DIR).replace("\\", "/") # Normalizar separadores
                    md_file.write(f"### `{relative_file_path}`\n\n")
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size == 0:
                             md_file.write("*Archivo vacío.*\n\n")
                             continue
                        if file_size > MAX_FILE_SIZE_CONTENT:
                            md_file.write(f"*Archivo demasiado grande ({file_size / 1024:.1f} KB) para incluir contenido completo.*\n\n")
                            continue
                            
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            lang = get_language_hint(filename)
                            md_file.write(f"```{lang}\n")
                            md_file.write(content)
                            md_file.write("\n```\n\n")
                    except UnicodeDecodeError:
                         md_file.write(f"*No se pudo leer el archivo (error de codificación). Podría ser un binario.*\n\n")
                    except Exception as e:
                        md_file.write(f"*Error al leer el archivo: {e}*\n\n")
                    
                    md_file.write("---\n\n") # Separador entre archivos

    print(f"¡Resumen generado exitosamente en '{OUTPUT_FILENAME}'!")

except Exception as e:
    print(f"Ocurrió un error al generar el resumen: {e}")
```

---

### `asm/gini_calculator.asm`

```assembly
; Archivo: TP2/asm/gini_calculator.asm
; Autor: [Tu Nombre/Grupo]
; Fecha: [Fecha Actual]
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
```

---

### `python/main.py`

```python
import requests
import ctypes
import os
import sys
from msl.loadlib import LoadLibrary # Usar msl-loadlib para cargar la lib 32 bits

# --- Configuración ---
# URL de la API del Banco Mundial para el índice GINI de Argentina (ARG)
API_URL = "https://api.worldbank.org/v2/country/ARG/indicator/SI.POV.GINI?format=json&date=2011:2023&per_page=100"

# Nombre y ruta de la biblioteca C compartida (32 bits)
LIB_NAME = 'libgini_processor.so' 
# Construye la ruta relativa a la carpeta lib/ desde python/
LIB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', LIB_NAME)

# --- Funciones ---

def fetch_latest_gini():
    """
    Obtiene el valor más reciente del índice GINI para Argentina desde la API del Banco Mundial.

    Returns:
        float: El valor GINI más reciente encontrado, o None si ocurre un error.
    """
    print(f"Consultando API: {API_URL}")
    try:
        response = requests.get(API_URL, timeout=10) # Añadir timeout
        response.raise_for_status() # Lanza excepción si hay error HTTP (4xx o 5xx)
        
        data = response.json()
        
        # La API devuelve una lista, el primer elemento [0] es metadata, el [1] son los datos
        if len(data) < 2 or not data[1]:
            print("Error: No se encontraron datos de indicadores en la respuesta de la API.")
            return None

        # Buscar el valor no nulo más reciente
        latest_value = None
        latest_year = 0
        for entry in data[1]:
            if entry.get('value') is not None: # Usar .get() para seguridad
                try:
                    year = int(entry['date'])
                    value = float(entry['value'])
                    if year > latest_year:
                        latest_year = year
                        latest_value = value
                except (ValueError, TypeError):
                    # Ignorar entradas con formato inválido
                    continue 
        
        if latest_value is not None:
            print(f"Valor GINI más reciente encontrado ({latest_year}): {latest_value:.2f}")
            return latest_value 
        else:
            print("Error: No se encontraron valores GINI válidos en el rango de fechas.")
            return None

    except requests.exceptions.Timeout:
        print(f"Error: Timeout al conectar con la API.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return None
    except (ValueError, IndexError, TypeError, KeyError) as e:
         print(f"Error procesando la respuesta JSON: {e}")
         return None


def call_c_function(gini_float):
    """
    Carga la biblioteca C de 32 bits y llama a la función process_gini_c 
    usando msl-loadlib.

    Args:
        gini_float (float): El valor GINI a procesar.

    Returns:
        int: El resultado devuelto por la función C (que llama a ASM), o None si falla.
    """
    if gini_float is None:
        print("No se puede llamar a la función C sin un valor GINI válido.")
        return None
            
    try:
        print(f"Cargando biblioteca C (32-bit) desde: {LIB_PATH} usando msl-loadlib")
        
        # Cargar la biblioteca usando LoadLibrary especificando arquitectura 32 bits y convención cdecl
        # Usar 'with' para asegurar la correcta liberación de recursos del servidor 32 bits
        with LoadLibrary(LIB_PATH, libtype='cdll') as lib_wrapper:
            lib_c = lib_wrapper.lib # Acceder al objeto library real

            # Definir el prototipo de la función C/ASM
            process_gini_func = lib_c.process_gini_c
            process_gini_func.argtypes = [ctypes.c_float]
            process_gini_func.restype = ctypes.c_int
            
            # Llamar a la función C (que llamará a ASM)
            print(f"Llamando a C/ASM: process_gini_c({gini_float:.2f})")
            result_int = process_gini_func(ctypes.c_float(gini_float))
            
            print(f"Resultado recibido de C/ASM: {result_int}")
            return result_int

    except FileNotFoundError:
        print(f"Error Crítico: No se encontró la biblioteca C en '{LIB_PATH}'.")
        print("Verifica que la ruta sea correcta y que hayas compilado la biblioteca (ej. 'make all').")
        return None
    except Exception as e: # Captura otros errores de msl-loadlib o ctypes
        print(f"Error al cargar o interactuar con la biblioteca C '{LIB_PATH}': {e}")
        print("Asegúrate de haber compilado la biblioteca C correctamente (32 bits),")
        print("tener 'msl-loadlib' instalado y un intérprete Python de 32 bits disponible en el sistema.")
        return None

# --- Ejecución Principal ---

if __name__ == "__main__":
    print("--- Iniciando TP2 Sistemas de Computación ---")
    
    # 1. Obtener datos de la API
    gini_value = fetch_latest_gini()
    
    # 2. Si obtuvimos datos, llamar a la función C/ASM
    if gini_value is not None:
        final_result = call_c_function(gini_value)
        
        if final_result is not None:
            print(f"\n>> Resultado final (GINI {gini_value:.2f} procesado por C->ASM): {final_result}")
        else:
            print("\n>> No se pudo obtener el resultado final de la función C/ASM.")
    else:
        print("\n>> No se pudo obtener el valor GINI de la API.")
        
    print("\n--- Fin TP2 ---")
```

---

### `c/debug_main.c`

```c
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
```

---

### `c/gini_processor.c`

```c
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
```

---

### `c/gini_processor.h`

```c
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
```

---

