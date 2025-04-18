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
	@$(PRINTF_CMD) '%s\n' 'printf "\n=== Breakpoints Set Automatically ===\n"' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'printf "%s", "Use '\''run'\'' to start, '\''c'\'' to continue, '\''ni'\''/'\''si'\'' for assembly steps. \n"' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'printf "%s", "Inspect stack: '\''x/16xw \$\$esp'\'' or '\''x/8xw \$\$ebp'\'' (after prologue) \n"' >> $(GDB_SCRIPT)
	@$(PRINTF_CMD) '%s\n' 'printf "%s", "Inspect registers: '\''info registers eax ebp esp'\''\n\\n"' >> $(GDB_SCRIPT)


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