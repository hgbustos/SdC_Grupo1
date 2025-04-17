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