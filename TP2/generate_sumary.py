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