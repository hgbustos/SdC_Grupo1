# Resumen del Proyecto TP2

```
TP2 (Raíz)/
  |-- Consigna.txt
  |-- Makefile
  |-- Readme.md
  |-- gdb_init_commands.txt
  |-- generate_sumary.py
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
```

---

## Contenido de Archivos

### `Makefile`

```makefile
# Makefile para el TP2 de Sistemas de Computación
# Compilación cruzada Python(64) -> C/ASM(32) y Debug App (32)
# INCLUYE: Generación de script GDB usando printf de GDB con escapes correctos

# --- Herramientas ---
NASM = nasm
CC = gcc
PYTHON = python3
GDB = gdb
PRINTF_CMD = printf # Comando printf del shell para generar el script

# --- Flags ---
ASMFLAGS = -f elf -g -F dwarf
COBJFLAGS = -m32 -g -Wall -c -O0
CFLAGS_SO = $(COBJFLAGS) -fPIC
LDFLAGS_SO = -m32 -shared -g
LDFLAGS_EXE = -m32 -g

# --- Directorios ---
SRC_DIR_C = c
SRC_DIR_ASM = asm
SRC_DIR_PY = python
OBJ_DIR = obj
LIB_DIR = lib
BIN_DIR = bin

# --- Archivos Fuente ---
C_SOURCES_LIB = $(filter-out $(SRC_DIR_C)/debug_main.c, $(wildcard $(SRC_DIR_C)/*.c))
ASM_SOURCES = $(wildcard $(SRC_DIR_ASM)/*.asm)
C_DEBUG_SOURCE = $(SRC_DIR_C)/debug_main.c
PY_MAIN = $(SRC_DIR_PY)/main.py
PY_MAIN_32 = $(SRC_DIR_PY)/main32.py

# --- Archivos Objeto ---
C_OBJS_LIB = $(patsubst $(SRC_DIR_C)/%.c, $(OBJ_DIR)/%.o, $(C_SOURCES_LIB))
ASM_OBJS = $(patsubst $(SRC_DIR_ASM)/%.asm, $(OBJ_DIR)/%.o, $(ASM_SOURCES))

# --- Archivos de Salida ---
LIB_TARGET = $(LIB_DIR)/libgini_processor.so
DEBUG_TARGET = $(BIN_DIR)/debug_app

# --- Archivos de Configuración GDB ---
GDB_SCRIPT = gdb_init_commands.txt

# --- Reglas ---

all: $(LIB_TARGET) $(DEBUG_TARGET)

# --- Reglas de Construcción de Archivos ---
# (Sin cambios)
$(LIB_TARGET): $(C_OBJS_LIB) $(ASM_OBJS)
	@echo "MKDIR (if needed) -> $(LIB_DIR)"
	@mkdir -p $(LIB_DIR)
	@echo "LD (Shared Lib) -> $@"
	$(CC) $(LDFLAGS_SO) -o $@ $^

$(DEBUG_TARGET): $(C_DEBUG_SOURCE) $(ASM_OBJS)
	@echo "MKDIR (if needed) -> $(BIN_DIR)"
	@mkdir -p $(BIN_DIR)
	@echo "LD (Debug App) -> $@"
	$(CC) $(LDFLAGS_EXE) -o $@ $^

$(OBJ_DIR)/gini_processor.o: $(SRC_DIR_C)/gini_processor.c $(SRC_DIR_C)/gini_processor.h
	@echo "MKDIR (if needed) -> $(OBJ_DIR)"
	@mkdir -p $(OBJ_DIR)
	@echo "CC (PIC Object) -> $@"
	$(CC) $(CFLAGS_SO) $< -o $@

$(OBJ_DIR)/%.o: $(SRC_DIR_ASM)/%.asm
	@echo "MKDIR (if needed) -> $(OBJ_DIR)"
	@mkdir -p $(OBJ_DIR)
	@echo "ASM -> $@"
	$(NASM) $(ASMFLAGS) $< -o $@


# --- Mejoras para Depuración (printf de GDB con escapes CORRECTOS) ---

$(GDB_SCRIPT):
	@echo "Generating GDB initialization script (Corrected GDB printf escapes): $(GDB_SCRIPT)"
	@$(PRINTF_CMD) '%s\n' '# Auto-generated GDB commands by Makefile' > $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# Breakpoints for analyzing C <-> ASM call in $(DEBUG_TARGET)' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# Set disassembly flavor to Intel syntax (like NASM)' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'set disassembly-flavor intel' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# Breakpoint in C, BEFORE calling ASM' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'break debug_main.c:29' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# Breakpoint at the START of the ASM function' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'break asm/gini_calculator.asm:22' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# Breakpoint in C, AFTER returning from ASM' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'break debug_main.c:33' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# Show defined breakpoints' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'info break' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# Optional: Automatically set a useful layout' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# layout split' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' '# Inform the user via GDB printf command' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'printf "\\n=== Breakpoints Set Automatically ===\\n"' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'printf "%s", "Use '\''run'\'' to start, '\''c'\'' to continue, '\''ni'\''/'\''si'\'' for assembly steps.\\n"' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'printf "%s", "Inspect stack: '\''x/16xw \$\$esp'\'' or '\''x/8xw \$\$ebp'\'' (after prologue)\\n"' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'printf "%s", "Inspect registers: '\''info registers eax ebp esp'\''\\n\\n"' >> $(GDB_SCRIPT)


debug: $(DEBUG_TARGET) $(GDB_SCRIPT)
	@echo "=== Iniciando GDB para $(DEBUG_TARGET) con comandos desde $(GDB_SCRIPT) ==="
	$(GDB) -q -x $(GDB_SCRIPT) $(DEBUG_TARGET)

# --- Reglas de Acciones (Phony) ---
# (Sin cambios)
run: $(LIB_TARGET)
	@echo "=== Ejecutando Script Python $(PY_MAIN) ==="
	$(PYTHON) $(PY_MAIN)

run32: $(LIB_TARGET)
	@echo "=== Ejecutando Script Python 32 bits (ctypes) $(PY_MAIN_32) ==="
	$(PYTHON) $(PY_MAIN_32)

clean:
	@echo "Limpiando directorios: $(OBJ_DIR) $(LIB_DIR) $(BIN_DIR)"
	@rm -rf $(OBJ_DIR) $(LIB_DIR) $(BIN_DIR)
	@echo "Eliminando script GDB: $(GDB_SCRIPT)"
	@rm -f $(GDB_SCRIPT)
	@echo "Limpieza completada."

.PHONY: all run run32 debug clean
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

### `python/main.py`

```python
# python/main.py (Modificado a Client64)
import requests
import os
import sys
import platform
from typing import Optional

# --- Importar Client64 de msl-loadlib ---
try:
    from msl.loadlib import Client64
    from msl.loadlib.exceptions import Server32Error
except ImportError:
    print("ERROR: 'msl-loadlib' no está instalado en el entorno 64-bit.")
    print("Ejecuta: pip install msl-loadlib")
    sys.exit(1)

# --- Configuración API (sin cambios) ---
API_URL = "https://api.worldbank.org/v2/country/ARG/indicator/SI.POV.GINI?format=json&date=2011:2023&per_page=100"

# --- Configuración Cliente 64-bit ---
# Nombre del MÓDULO Python que contiene la clase Server32 (sin .py)
# Debe apuntar al archivo que creaste en el paso 1
SERVER_MODULE_NAME = 'server32_bridge' # Asumiendo que está en la misma carpeta python/
# Método que definiste en GiniProcessorServer32 para manejar la petición
SERVER_METHOD_NAME = 'process_gini_request'

# --- Clase Cliente 64-bit ---
class GiniClient(Client64):
    def __init__(self):
        print(f"INFO [Client64]: Inicializando cliente...")
        print(f"INFO [Client64]: Python Arch: {platform.architecture()[0]}", file=sys.stderr) # Debe ser 64bit
        try:
            # Apunta al módulo del servidor 32-bit
            super().__init__(module32=SERVER_MODULE_NAME)
            print(f"INFO [Client64]: Conectado a servidor 32-bit '{SERVER_MODULE_NAME}'.")
        except Exception as e:
             print(f"FATAL ERROR [Client64]: al inicializar: {type(e).__name__}: {e}", file=sys.stderr)
             print(f"Verifica que Python 32-bit esté instalado y sea accesible, y que '{SERVER_MODULE_NAME}.py' no tenga errores.", file=sys.stderr)
             raise

    def call_process_gini(self, gini_value: float) -> Optional[int]:
        """Envía petición al método del servidor 32-bit."""
        print(f"INFO [Client64]: Enviando petición '{SERVER_METHOD_NAME}' con valor: {gini_value}")
        try:
            # Llama al método remoto definido en SERVER_METHOD_NAME
            result = self.request32(SERVER_METHOD_NAME, gini_value)
            print(f"INFO [Client64]: Respuesta recibida del servidor: {result}")
            return result
        except Server32Error as e:
            print(f"ERROR [Client64]: Error recibido del servidor 32-bit: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"ERROR [Client64]: Error de comunicación: {type(e).__name__}: {e}", file=sys.stderr)
            return None

# --- Instancia Singleton del Cliente ---
_gini_client_instance = None

def get_client() -> Optional[GiniClient]:
    global _gini_client_instance
    if _gini_client_instance is None:
        try:
            _gini_client_instance = GiniClient()
        except Exception:
             # El error ya se imprimió en __init__
             _gini_client_instance = None # Asegura que siga None
    return _gini_client_instance

# --- Funciones fetch_latest_gini (sin cambios) ---
def fetch_latest_gini():
    # ... (tu código existente para la API) ...
    print(f"Consultando API: {API_URL}")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if len(data) < 2 or not data[1]:
            print("Error: No se encontraron datos de indicadores.")
            return None
        latest_value = None
        latest_year = 0
        for entry in data[1]:
            if entry.get('value') is not None:
                try:
                    year = int(entry['date'])
                    value = float(entry['value'])
                    if year > latest_year:
                        latest_year = year
                        latest_value = value
                except (ValueError, TypeError): continue
        if latest_value is not None:
            print(f"Valor GINI más reciente ({latest_year}): {latest_value:.2f}")
            return latest_value
        else:
            print("Error: No se encontraron valores GINI válidos.")
            return None
    except Exception as e:
        print(f"Error en API o JSON: {e}")
        return None

# --- Función para llamar a C/ASM vía Cliente/Servidor ---
def call_c_asm_via_client(gini_float):
    if gini_float is None:
         print("Valor GINI inválido, no se puede procesar.")
         return None

    client = get_client()
    if client is None:
         print("ERROR: Cliente 64-bit no disponible. No se puede procesar.")
         return None

    # Llama al método del cliente que hace la petición al servidor
    result_int = client.call_process_gini(gini_float)
    return result_int

# --- Ejecución Principal ---
if __name__ == "__main__":
    print("--- Iniciando TP2 (Client/Server) ---")
    gini_value = fetch_latest_gini()

    if gini_value is not None:
        final_result = call_c_asm_via_client(gini_value)
        if final_result is not None:
            print(f"\n>> Resultado final (GINI {gini_value:.2f} procesado por C->ASM vía Server32): {final_result}")
        else:
            print("\n>> Fallo al obtener resultado del procesamiento C/ASM.")
    else:
        print("\n>> No se pudo obtener el valor GINI de la API.")

    # Opcional: Cerrar explícitamente el cliente/servidor si es necesario
    # client = get_client()
    # if client: client.shutdown_server32()

    print("\n--- Fin TP2 ---")
```

---

### `python/main32.py`

```python
# Archivo: python/main32.py
# Descripción: Versión del script principal para ejecutar en un entorno Python 32 bits.
#              Utiliza la librería estándar 'ctypes' para cargar la biblioteca C 32 bits.
#              (No requiere msl-loadlib).

import requests
import ctypes # <--- Se usa ctypes estándar
import os
import sys

# --- Configuración ---
# URL de la API del Banco Mundial para el índice GINI de Argentina (ARG)
API_URL = "https://api.worldbank.org/v2/country/ARG/indicator/SI.POV.GINI?format=json&date=2011:2023&per_page=100"

# Nombre y ruta de la biblioteca C compartida (32 bits)
# Asume que este script está en TP2/python/ y la lib en TP2/lib/
LIB_NAME = 'libgini_processor.so' 
LIB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', LIB_NAME)

# --- Funciones ---

def fetch_latest_gini():
    """
    Obtiene el valor más reciente del índice GINI para Argentina desde la API del Banco Mundial.
    (Esta función es idéntica a la versión original)

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
    usando ctypes estándar (adecuado para Python 32 bits cargando lib 32 bits).

    Args:
        gini_float (float): El valor GINI a procesar.

    Returns:
        int: El resultado devuelto por la función C (que llama a ASM), o None si falla.
    """
    if gini_float is None:
        print("No se puede llamar a la función C sin un valor GINI válido.")
        return None
            
    try:
        print(f"Cargando biblioteca C (32-bit) desde: {LIB_PATH} usando ctypes")
        
        # --- Carga directa con ctypes.CDLL ---
        # Verifica si la librería existe antes de intentar cargarla
        if not os.path.exists(LIB_PATH):
             raise FileNotFoundError(f"No se encontró la biblioteca en: {LIB_PATH}")

        lib_c = ctypes.CDLL(LIB_PATH) 
        # --------------------------------------

        # Definir el prototipo de la función C/ASM (sigue igual)
        # Asegúrate que el nombre '_process_gini_c' coincida con el exportado por tu lib C
        process_gini_func = lib_c.process_gini_c 
        process_gini_func.argtypes = [ctypes.c_float]
        process_gini_func.restype = ctypes.c_int
        
        # Llamar a la función C (sigue igual)
        print(f"Llamando a C/ASM: process_gini_c({gini_float:.2f})")
        result_int = process_gini_func(ctypes.c_float(gini_float))
        
        print(f"Resultado recibido de C/ASM: {result_int}")
        return result_int

    except FileNotFoundError as e:
        print(f"Error Crítico: {e}")
        print("Verifica que la ruta sea correcta y que hayas compilado la biblioteca (ej. 'make all').")
        return None
    except OSError as e: # ctypes lanza OSError si hay problemas al cargar (ej: dependencias faltantes, formato incorrecto)
        print(f"Error al cargar o enlazar la biblioteca C '{LIB_PATH}' con ctypes: {e}")
        print("Asegúrate de haber compilado la biblioteca C correctamente para 32 bits.")
        return None
    except AttributeError as e: # Si la función 'process_gini_c' no se encuentra en la lib
        print(f"Error: No se encontró la función 'process_gini_c' en la biblioteca '{LIB_NAME}'. {e}")
        print("Verifica que la función esté declarada como 'extern' en C y exportada correctamente.")
        return None
    except Exception as e: # Captura otros errores inesperados
        print(f"Error inesperado al interactuar con la biblioteca C: {e}")
        return None

# --- Ejecución Principal ---
# (Esta parte es idéntica a la versión original)

if __name__ == "__main__":
    print("--- Iniciando TP2 Sistemas de Computación (Versión 32 bits) ---")
    
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
        
    print("\n--- Fin TP2 (Versión 32 bits) ---")
```

---

### `python/server32_bridge.py`

```python
# python/server32_bridge.py (Adaptado para TU C/ASM)
import os
import ctypes
import sys
import platform

try:
    from msl.loadlib import Server32
except ImportError:
    print("ERROR [Server32]: msl-loadlib no encontrado en entorno Python 32-bit.", file=sys.stderr)
    sys.exit(1)

# --- Configuración ---
LIB_FILENAME = 'libgini_processor.so'
# El nombre de TU función C wrapper
C_FUNCTION_NAME = 'process_gini_c' # <--- TU función

# Ruta a TU librería (asumiendo que server32_bridge está en python/)
SERVER_DIR = os.path.dirname(__file__)
# Sube un nivel desde 'python' para llegar a 'TP2', luego entra a 'lib'
LIB_DIR = os.path.abspath(os.path.join(SERVER_DIR, '..', 'lib'))
LIBRARY_PATH = os.path.join(LIB_DIR, LIB_FILENAME)

print(f"INFO [Server32]: Intentando cargar lib desde: {LIBRARY_PATH}", file=sys.stderr)

class GiniProcessorServer32(Server32):
    def __init__(self, host, port, **kwargs):
        print(f"INFO [Server32]: Inicializando servidor...", file=sys.stderr)
        print(f"INFO [Server32]: Python Arch: {platform.architecture()[0]}", file=sys.stderr) # Debe ser 32bit

        if not os.path.exists(LIBRARY_PATH):
             error_msg = f"FATAL ERROR [Server32]: Librería '{LIBRARY_PATH}' no encontrada."
             print(error_msg, file=sys.stderr)
             raise FileNotFoundError(error_msg)

        try:
            # Carga TU librería (asumiendo cdecl)
            super().__init__(LIBRARY_PATH, 'cdll', host, port, **kwargs)
            print(f"INFO [Server32]: Librería '{LIB_FILENAME}' cargada.", file=sys.stderr)

            # --- Definir firma de TU función C ---
            c_func = getattr(self.lib, C_FUNCTION_NAME)
            # TU función recibe un float
            c_func.argtypes = [ctypes.c_float]
            # TU función devuelve un int
            c_func.restype = ctypes.c_int
            print(f"INFO [Server32]: Firma definida para '{C_FUNCTION_NAME}'.", file=sys.stderr)

        except Exception as e:
            print(f"ERROR [Server32]: durante inicialización: {type(e).__name__}: {e}", file=sys.stderr)
            raise

    # --- Método expuesto al Client64 ---
    # El nombre debe coincidir con lo que llama el cliente
    def process_gini_request(self, gini_float_value):
        print(f"INFO [Server32]: Recibida petición process_gini_request({gini_float_value})", file=sys.stderr)
        try:
            # Llama a TU función C 'process_gini_c'
            result = self.lib.process_gini_c(ctypes.c_float(gini_float_value))
            print(f"INFO [Server32]: Función C devolvió: {result}", file=sys.stderr)
            return result # Devuelve el int al Client64
        except Exception as e:
            print(f"ERROR [Server32]: al llamar a C '{C_FUNCTION_NAME}': {type(e).__name__}: {e}", file=sys.stderr)
            raise # Propaga error al cliente
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
    printf("     Aqui se debe inspeccionar pila (esp) y registros (ebp) aquí.\n");
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

### `asm/gini_calculator.asm`

```assembly
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
```

---

