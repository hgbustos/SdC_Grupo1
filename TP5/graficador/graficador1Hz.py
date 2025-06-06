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
MAX_DATA_POINTS = 50 # Número de puntos a mostrar en el gráfico

# --- Variables Globales ---
data_buffer = deque(maxlen=MAX_DATA_POINTS) 
current_sensor_label = "Ninguno" # Qué sensor estamos mostrando actualmente
keep_running = True # Una bandera para detener hilos de forma segura

# --- Hilo Lector (se ejecuta en segundo plano) ---
def serial_reader():
    """
    Este hilo se conecta al puerto serie y continuamente lee líneas.
    Añade los datos recibidos (etiqueta y valor) al buffer global.
    """
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
                        # Guardamos un diccionario con la etiqueta y el valor
                        data_buffer.append({'label': label, 'value': int(value_str)})
                except (ValueError, UnicodeDecodeError):
                    # Ignora líneas corruptas o incompletas sin detenerse
                    pass 
            time.sleep(0.05) # Pequeña pausa para no sobrecargar la CPU
        ser.close()
        print("Hilo lector ha cerrado el puerto serie.")
    except serial.SerialException as e:
        print(f"Error Crítico del Puerto Serie: {e}")
        print("Asegúrate de que el ESP32 esté conectado y que nadie más use el puerto.")
        keep_running = False

# --- Función de Graficado (Llamada periódicamente por Matplotlib) ---
def update_plot(frame):
    """
    Esta función se ejecuta para cada "frame" de la animación.
    Limpia el gráfico y dibuja solo los puntos del sensor seleccionado.
    """
    # Filtramos del buffer solo los puntos que coinciden con la etiqueta seleccionada
    points_to_plot = [item['value'] for item in list(data_buffer) if item['label'] == current_sensor_label]
    
    ax.clear() # Limpia el gráfico anterior para redibujar
    if points_to_plot:
        ax.plot(points_to_plot, marker='o', linestyle='-') # Dibuja los puntos
    
    # Configura las etiquetas y el título del gráfico
    ax.set_title(f'Sensor: {current_sensor_label}')
    ax.set_ylabel('Valor ADC (0-4095)')
    ax.set_xlabel(f'Últimas {len(points_to_plot)} muestras (a 1Hz)')
    ax.set_ylim(-100, 4200) # Fija el eje Y para que la escala no "salte"
    ax.grid(True)
    
# --- Funciones de Control (Llamadas desde los botones) ---
def select_sensor(label_to_select):
    """
    Esta función se activa cuando se presiona un botón.
    Actualiza la etiqueta global y envía el comando correspondiente al driver.
    """
    global current_sensor_label
    print(f"Botón presionado. Seleccionando sensor: {label_to_select}...")
    current_sensor_label = label_to_select
    
    command = "S1" if label_to_select == "LDR" else "S2"
    try:
        # Abre, escribe y cierra el archivo del driver.
        with open(DRIVER_PATH, 'w') as f:
            f.write(command)
        print(f"Comando '{command}' enviado al driver {DRIVER_PATH} exitosamente.")
    except IOError as e:
        print(f"ERROR: No se pudo escribir en el driver {DRIVER_PATH}: {e}")
        print("Asegúrate de que el módulo 'sensor_driver.ko' esté cargado.")

# --- Punto de Entrada del Script ---
if _name_ == '_main_':
    # 1. Iniciar el hilo lector que llenará el buffer en segundo plano.
    reader_thread = Thread(target=serial_reader, daemon=True)
    reader_thread.start()

    # 2. Configurar la ventana y los ejes de Matplotlib.
    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title('TP SdeC - Graficador de Señales')
    fig.subplots_adjust(bottom=0.25) # Hacemos espacio abajo para los botones.

    # 3. Crear los botones de control.
    # [left, bottom, width, height], como porcentajes de la figura.
    ax_btn_ldr = plt.axes([0.2, 0.05, 0.25, 0.1])
    btn_ldr = Button(ax_btn_ldr, 'Leer LDR (S1)')
    # Conectamos el evento 'on_clicked' del botón a nuestra función.
    btn_ldr.on_clicked(lambda event: select_sensor('LDR'))

    ax_btn_pot = plt.axes([0.55, 0.05, 0.25, 0.1])
    btn_pot = Button(ax_btn_pot, 'Leer POT (S2)')
    btn_pot.on_clicked(lambda event: select_sensor('POT'))
    
    # 4. Iniciar la animación que llamará a update_plot cada 500ms.
    ani = animation.FuncAnimation(fig, update_plot, interval=500)
    
    print("Ventana de control lista. Usa los botones para seleccionar un sensor.")
    
    # 5. Mostrar la ventana. Esta llamada es bloqueante.
    plt.show()

    # 6. Código de limpieza cuando la ventana se cierra.
    print("Ventana cerrada. Finalizando la aplicación...")
    keep_running = False
    if reader_thread.is_alive():
        reader_thread.join(timeout=1) # Esperamos un poco a que el hilo termine.
    
    print("Aplicación terminada limpiamente.")