# --- graficador_fluido.py ---
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
from threading import Thread
import time
from collections import deque

# --- Configuración ---
SERIAL_PORT = '/dev/ttyUSB0'
DRIVER_PATH = '/dev/sensor_cdd'
BAUD_RATE = 115200

# --- CAMBIOS PARA FLUIDEZ ---
MAX_DATA_POINTS = 100 # Aumentamos el buffer para tener más historial (100 puntos a 20Hz = 5s)
ANIMATION_INTERVAL = 50 # Actualizamos el gráfico cada 50ms

# --- Variables Globales ---
data_buffer = deque(maxlen=MAX_DATA_POINTS) 
current_sensor_label = "Ninguno"
keep_running = True

# --- Hilo Lector (No necesita cambios) ---
def serial_reader():
    global data_buffer, keep_running
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"Hilo lector conectado a {SERIAL_PORT}.")
        while keep_running:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if ':' in line:
                        label, value_str = line.split(':')
                        data_buffer.append({'label': label, 'value': int(value_str)})
                except (ValueError, UnicodeDecodeError): pass 
            time.sleep(0.01) # Pausa mínima, ya que el intervalo del ESP32 domina
        ser.close()
        print("Hilo lector ha cerrado el puerto serie.")
    except serial.SerialException as e:
        print(f"Error Crítico del Puerto Serie: {e}")
        keep_running = False

# --- Función de Graficado (Con etiqueta de eje X actualizada) ---
def update_plot(frame):
    points_to_plot = [item['value'] for item in list(data_buffer) if item['label'] == current_sensor_label]
    
    ax.clear()
    if points_to_plot:
        ax.plot(points_to_plot, linestyle='-') # Quitamos el marcador para una línea más limpia
    
    ax.set_title(f'Sensor: {current_sensor_label} (Modo Fluido @20Hz)')
    ax.set_ylabel('Valor ADC (0-4095)')
    ax.set_xlabel(f'Muestras Recientes (hasta {MAX_DATA_POINTS} puntos)') # Etiqueta actualizada
    ax.set_ylim(-100, 4200)
    ax.grid(True)
    
# --- Funciones de Control (No necesitan cambios) ---
def select_sensor(label_to_select):
    global current_sensor_label
    print(f"Botón presionado. Seleccionando sensor: {label_to_select}...")
    current_sensor_label = label_to_select
    command = "S1" if label_to_select == "LDR" else "S2"
    try:
        with open(DRIVER_PATH, 'w') as f:
            f.write(command)
        print(f"Comando '{command}' enviado al driver {DRIVER_PATH} exitosamente.")
    except IOError as e:
        print(f"ERROR: No se pudo escribir en el driver {DRIVER_PATH}: {e}")

# --- Punto de Entrada del Script ---
if _name_ == '_main_':
    reader_thread = Thread(target=serial_reader, daemon=True)
    reader_thread.start()

    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title('TP SdeC - Graficador de Señales (Modo Fluido)')
    fig.subplots_adjust(bottom=0.25)

    ax_btn_ldr = plt.axes([0.2, 0.05, 0.25, 0.1])
    btn_ldr = Button(ax_btn_ldr, 'Leer LDR (S1)')
    btn_ldr.on_clicked(lambda event: select_sensor('LDR'))

    ax_btn_pot = plt.axes([0.55, 0.05, 0.25, 0.1])
    btn_pot = Button(ax_btn_pot, 'Leer POT (S2)')
    btn_pot.on_clicked(lambda event: select_sensor('POT'))
    
    # --- CAMBIO DE INTERVALO DE ANIMACIÓN ---
    ani = animation.FuncAnimation(fig, update_plot, interval=ANIMATION_INTERVAL)
    
    print("Ventana de control lista. Usa los botones para seleccionar un sensor.")
    plt.show()

    print("Ventana cerrada. Finalizando la aplicación...")
    keep_running = False
    if reader_thread.is_alive():
        reader_thread.join(timeout=1)
    
    print("Aplicación terminada limpiamente.")