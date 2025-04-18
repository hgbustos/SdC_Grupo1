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