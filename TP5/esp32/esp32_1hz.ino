/*
  ESP32 - Selector de Sensor y Envío Periódico

  Lee un potenciómetro (GPIO34) o un LDR (GPIO35).
  Selecciona cuál sensor enviar basado en comandos seriales:
  - "S1": Selecciona LDR
  - "S2": Selecciona Potenciómetro

  Envía el valor del sensor seleccionado cada SEGUNDO.
*/

// Definir los pines ADC
const int potPin = 34; // Pin para el potenciómetro
const int ldrPin = 35; // Pin para el LDR

// Variable para almacenar el sensor actualmente seleccionado
// 0 = Ninguno, 1 = LDR, 2 = Potenciómetro
int sensorSeleccionado = 0; // Por defecto, ninguno o podrías elegir uno.

// Variables para el manejo del tiempo con millis()
unsigned long tiempoAnterior = 0;
const long intervalo = 1000; // Intervalo de 1 segundo (1000 milisegundos)

String comandoSerial = ""; // String para almacenar el comando recibido

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 Sensor Selector Listo.");
  Serial.println("Enviar 'S1' para LDR o 'S2' para Potenciometro.");
  Serial.println("---------------------------------------------------");
  // sensorSeleccionado = 1; // Opcional: seleccionar un sensor por defecto al inicio
}

void loop() {
  // 1. Revisar si hay comandos seriales entrantes
  if (Serial.available() > 0) {
    char caracterEntrante = Serial.read(); // Leer un caracter
    if (caracterEntrante == '\n') { // Si es el fin de línea, procesar comando
      procesarComando(comandoSerial);
      comandoSerial = ""; // Limpiar el buffer del comando
    } else if (caracterEntrante != '\r') { // Ignorar retorno de carro, acumular otros caracteres
      comandoSerial += caracterEntrante;
    }
  }

  // 2. Comprobar si es tiempo de enviar datos (cada 'intervalo' milisegundos)
  unsigned long tiempoActual = millis();
  if (tiempoActual - tiempoAnterior >= intervalo) {
    tiempoAnterior = tiempoActual; // Guardar el último tiempo de envío

    if (sensorSeleccionado != 0) { // Solo enviar si un sensor está seleccionado
      enviarDatosSensor();
    }
  }
}

void procesarComando(String comando) {
  comando.trim(); // Quitar espacios en blanco al inicio/final
  Serial.print("Comando recibido: ");
  Serial.println(comando);

  if (comando.equalsIgnoreCase("S1")) {
    sensorSeleccionado = 1; // Seleccionar LDR
    Serial.println("Sensor LDR seleccionado. Enviando datos del LDR...");
  } else if (comando.equalsIgnoreCase("S2")) {
    sensorSeleccionado = 2; // Seleccionar Potenciómetro
    Serial.println("Sensor Potenciometro seleccionado. Enviando datos del Potenciometro...");
  } else {
    Serial.println("Comando no reconocido. Usar 'S1' o 'S2'.");
  }
}

void enviarDatosSensor() {
  int valorSensor = 0;
  String etiquetaSensor = "";

  if (sensorSeleccionado == 1) { // LDR
    valorSensor = analogRead(ldrPin);
    etiquetaSensor = "LDR";
  } else if (sensorSeleccionado == 2) { // Potenciómetro
    valorSensor = analogRead(potPin);
    etiquetaSensor = "POT";
  } else {
    return; // No hacer nada si no hay sensor seleccionado
  }

  // Formato de envío: "ETIQUETA:VALOR" (Ej: "LDR:1234" o "POT:2048")
  Serial.print(etiquetaSensor);
  Serial.print(":");
  Serial.println(valorSensor);
}