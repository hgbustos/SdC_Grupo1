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