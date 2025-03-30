#include <Arduino.h>

void ejecutarTest(int frecuenciaMHz) {
  Serial.print("\n--- Probando con frecuencia: ");
  Serial.print(frecuenciaMHz);
  Serial.println(" MHz ---");

  setCpuFrequencyMhz(frecuenciaMHz);
  delay(500);  // Esperar un poco para estabilizar

  // --------- Bucle de enteros ---------
  unsigned long tInicio = millis();
  volatile long sumaEnteros = 0;
  long repeticionesEnteros = 200000000; 

  for (long i = 0; i < repeticionesEnteros; i++) {
    sumaEnteros += i;
  }
  unsigned long tFin = millis();
  Serial.print("Tiempo enteros: ");
  Serial.print(tFin - tInicio);
  Serial.println(" ms");

  // --------- Bucle de floats ---------
  tInicio = millis();
  volatile float sumaFloats = 0.0;
  long repeticionesFloats = 50000000;

  for (long i = 0; i < repeticionesFloats; i++) {
    sumaFloats += 1.2345;
  }
  tFin = millis();
  Serial.print("Tiempo floats: ");
  Serial.print(tFin - tInicio);
  Serial.println(" ms");

  Serial.println("--- Fin del test para esta frecuencia ---\n");
  delay(2000);  // Pausa entre pruebas
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  delay(1000);
  Serial.println("Iniciando test automático de frecuencias...\n");

  int frecuencias[] = {80, 160, 240};

  for (int i = 0; i < 3; i++) {
    ejecutarTest(frecuencias[i]);
  }

  Serial.println("✅ Pruebas finalizadas.");
}

void loop() {
  // Nada
}
