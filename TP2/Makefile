# Makefile para el TP2 de Sistemas de Computación
# Compilación cruzada Python(64) -> C/ASM(32) y Debug App (32)

# --- Herramientas ---
NASM = nasm
CC = gcc
PYTHON = python3

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

# --- Archivos Objeto ---
C_OBJS_LIB = $(patsubst $(SRC_DIR_C)/%.c, $(OBJ_DIR)/%.o, $(C_SOURCES_LIB))
ASM_OBJS = $(patsubst $(SRC_DIR_ASM)/%.asm, $(OBJ_DIR)/%.o, $(ASM_SOURCES))

# --- Archivos de Salida ---
LIB_TARGET = $(LIB_DIR)/libgini_processor.so
DEBUG_TARGET = $(BIN_DIR)/debug_app

# --- Reglas ---

# Regla por defecto: construir la biblioteca compartida Y el ejecutable de debug
all: $(LIB_TARGET) $(DEBUG_TARGET)

# --- Reglas de Construcción de Archivos ---

# Construir la biblioteca compartida
$(LIB_TARGET): $(C_OBJS_LIB) $(ASM_OBJS)
	@echo "MKDIR (if needed) -> $(LIB_DIR)"
	@mkdir -p $(LIB_DIR) 
	@echo "LD (Shared Lib) -> $(LIB_TARGET)" # Usar variable explícita para echo
	$(CC) $(LDFLAGS_SO) -o $(LIB_TARGET) $(filter %.o,$^) # Usar variable explícita para -o

# Construir el ejecutable de depuración
$(DEBUG_TARGET): $(C_DEBUG_SOURCE) $(ASM_OBJS)
	@echo "MKDIR (if needed) -> $(BIN_DIR)"
	@mkdir -p $(BIN_DIR) 
	@echo "LD (Debug App) -> $(DEBUG_TARGET)" # Usar variable explícita para echo
	$(CC) $(LDFLAGS_EXE) -o $(DEBUG_TARGET) $(filter %.c %.o,$^) # ¡¡Usar variable explícita para -o!!

# Compilar objetos C para la biblioteca compartida
$(OBJ_DIR)/gini_processor.o: $(SRC_DIR_C)/gini_processor.c $(SRC_DIR_C)/gini_processor.h
	@echo "MKDIR (if needed) -> $(OBJ_DIR)"
	@mkdir -p $(OBJ_DIR) 
	@echo "CC (PIC Object) -> $@"
	$(CC) $(CFLAGS_SO) $< -o $@ # Aquí $@ debería funcionar para objetos .o

# Ensamblar objetos ASM
$(OBJ_DIR)/%.o: $(SRC_DIR_ASM)/%.asm
	@echo "MKDIR (if needed) -> $(OBJ_DIR)"
	@mkdir -p $(OBJ_DIR) 
	@echo "ASM -> $@"
	$(NASM) $(ASMFLAGS) $< -o $@ # Aquí $@ debería funcionar para objetos .o


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

# Phony targets
.PHONY: all run debug clean