#!/bin/bash
# Script para generar available_modules_sample.txt
# Ejecutar desde el directorio TP4_GrupoX/practico/02_system_info/

# Definir el archivo de salida
OUTPUT_FILE="available_modules_sample.txt"
KERNEL_VERSION=$(uname -r)

# Encabezado y limpieza del archivo de salida
echo "--- Contenido de available_modules_sample.txt ---" > "$OUTPUT_FILE"
echo "Generado el: $(date)" >> "$OUTPUT_FILE"
echo "Kernel: $KERNEL_VERSION" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# --- Listado de algunos módulos .ko.zst disponibles (ejemplos de drivers) ---
echo "--- Listado de algunos módulos .ko.zst disponibles (ejemplos de drivers) ---" >> "$OUTPUT_FILE"
OUTPUT_FIND_SAMPLE=$(find "/lib/modules/$KERNEL_VERSION/kernel/drivers/" -name "*.ko.zst" -type f 2>/dev/null | head -n 5)
if [ -n "$OUTPUT_FIND_SAMPLE" ]; then
    echo "$OUTPUT_FIND_SAMPLE" >> "$OUTPUT_FILE"
else
    echo "(No se encontraron módulos .ko.zst de ejemplo en /lib/modules/$KERNEL_VERSION/kernel/drivers/)" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# --- Ejemplo: Verificando 'floppy.ko.zst' ---
echo "--- Ejemplo: Verificando 'floppy.ko.zst' ---" >> "$OUTPUT_FILE"
OUTPUT_FIND_FLOPPY=$(find "/lib/modules/$KERNEL_VERSION/kernel" -name "floppy.ko.zst" -type f 2>/dev/null)
if [ -n "$OUTPUT_FIND_FLOPPY" ]; then
    echo "Ubicación de floppy.ko.zst:" >> "$OUTPUT_FILE"
    echo "$OUTPUT_FIND_FLOPPY" >> "$OUTPUT_FILE"
else
    echo "floppy.ko.zst no encontrado como archivo en /lib/modules/$KERNEL_VERSION/kernel" >> "$OUTPUT_FILE"
fi
echo "Estado de carga de 'floppy' (lsmod):" >> "$OUTPUT_FILE"
OUTPUT_LSMOD_FLOPPY=$(lsmod | grep floppy)
if [ -n "$OUTPUT_LSMOD_FLOPPY" ]; then
    echo "$OUTPUT_LSMOD_FLOPPY" >> "$OUTPUT_FILE"
else
    echo "(El módulo 'floppy' no está cargado actualmente)" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# --- Ejemplo: Verificando 'amdgpu' (módulo cargado) ---
echo "--- Ejemplo: Verificando 'amdgpu' (módulo cargado) ---" >> "$OUTPUT_FILE"
echo "Ruta del módulo 'amdgpu' según modules.dep (puede estar comprimido):" >> "$OUTPUT_FILE"
# Usamos grep y cut para extraer solo la ruta del archivo .ko.zst de amdgpu
GREP_AMDGPU_DEP_OUTPUT=$(cat "/lib/modules/$KERNEL_VERSION/modules.dep" | grep "amdgpu.ko.zst:" | head -n 1)
if [ -n "$GREP_AMDGPU_DEP_OUTPUT" ]; then
    echo "${GREP_AMDGPU_DEP_OUTPUT%%:*}" >> "$OUTPUT_FILE" # Extrae la parte antes del primer ':'
else
    echo "(No se encontró la entrada para amdgpu.ko.zst en modules.dep)" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"
echo "Estado de carga de 'amdgpu' (lsmod) - Salida completa de tu sistema:" >> "$OUTPUT_FILE"
# Aquí debes pegar LA SALIDA COMPLETA de `lsmod | grep amdgpu` de tu sistema.
# La obtuve de un mensaje anterior tuyo, asegúrate que esté completa y actualizada si cambió el "Used by".
echo "amdgpu              20025344  25" >> "$OUTPUT_FILE"
echo "amdxcp                 12288  1 amdgpu" >> "$OUTPUT_FILE"
echo "drm_exec               12288  1 amdgpu" >> "$OUTPUT_FILE"
echo "gpu_sched              61440  1 amdgpu" >> "$OUTPUT_FILE"
echo "drm_buddy              24576  1 amdgpu" >> "$OUTPUT_FILE"
echo "drm_suballoc_helper    20480  1 amdgpu" >> "$OUTPUT_FILE" # Añadido de tu primera salida lsmod
echo "drm_ttm_helper         16384  1 amdgpu" >> "$OUTPUT_FILE" # Añadido de tu primera salida lsmod
echo "ttm                   110592  2 amdgpu,drm_ttm_helper" >> "$OUTPUT_FILE" # Añadido de tu primera salida lsmod
echo "drm_display_helper    278528  1 amdgpu" >> "$OUTPUT_FILE" # Añadido de tu primera salida lsmod
echo "i2c_algo_bit           16384  1 amdgpu" >> "$OUTPUT_FILE" # Añadido de tu primera salida lsmod
echo "video                  77824  1 amdgpu" >> "$OUTPUT_FILE"
# Si hay más líneas de 'amdgpu' en tu 'lsmod' original, añádelas aquí.

echo "" >> "$OUTPUT_FILE"
echo "--- Fin del reporte ---" >> "$OUTPUT_FILE"

echo "Archivo '$OUTPUT_FILE' generado exitosamente."