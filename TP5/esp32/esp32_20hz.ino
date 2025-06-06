/*
  ESP32 - Selector de Sensor y Envío Periódico (Alta Frecuencia)

  Lee un potenciómetro (GPIO34) o un LDR (GPIO35).
  Selecciona cuál sensor enviar basado en comandos seriales.
  Envía el valor del sensor seleccionado a alta frecuencia.
*/

const int potPin = 34;
const int ldrPin = 35;
int sensorSeleccionado = 0;
unsigned long tiempoAnterior = 0;

const long intervalo = 50; 

String comandoSerial = "";

void setup() {
  Serial.begin(115200); // Mantenemos la velocidad por ahora
  delay(1000);

  Serial.println("ESP32 Sensor Selector Listo (Modo Fluido @20Hz).");
  Serial.println("Enviar 'S1' para LDR o 'S2' para Potenciometro.");
  Serial.println("---------------------------------------------------");
}

void loop() {
  if (Serial.available() > 0) {
    char caracterEntrante = Serial.read();
    if (caracterEntrante == '\n') {
      procesarComando(comandoSerial);
      comandoSerial = "";
    } else if (caracterEntrante != '\r') {
      comandoSerial += caracterEntrante;
    }
  }

  unsigned long tiempoActual = millis();
  if (tiempoActual - tiempoAnterior >= intervalo) {
    tiempoAnterior = tiempoActual;
    if (sensorSeleccionado != 0) {
      enviarDatosSensor();
    }
  }
}

void procesarComando(String comando) {
  comando.trim();
  Serial.print("Comando recibido: ");
  Serial.println(comando);
  if (comando.equalsIgnoreCase("S1")) {
    sensorSeleccionado = 1;
    Serial.println("Sensor LDR seleccionado.");
  } else if (comando.equalsIgnoreCase("S2")) {
    sensorSeleccionado = 2;
    Serial.println("Sensor Potenciometro seleccionado.");
  } else {
    Serial.println("Comando no reconocido.");
  }
}

void enviarDatosSensor() {
  int valorSensor = 0;
  String etiquetaSensor = "";

  if (sensorSeleccionado == 1) {
    valorSensor = analogRead(ldrPin);
    etiquetaSensor = "LDR";
  } else if (sensorSeleccionado == 2) {
    valorSensor = analogRead(potPin);
    etiquetaSensor = "POT";
  } else {
    return;
  }
  
  Serial.print(etiquetaSensor);
  Serial.print(":");
  Serial.println(valorSensor);
}