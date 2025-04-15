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