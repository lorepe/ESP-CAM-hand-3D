#include <Servo.h>

// Crear arreglo de servos para los 5 dedos
Servo dedos[5];

// Pines PWM asignados a cada dedo
int pines[5] = {3, 5, 6, 9, 10};  // Pulgar, Índice, Medio, Anular, Meñique

// Rango máximo para cada dedo (meñique se mueve más)
int maxAngulo[5] = {180, 180, 180, 180, 200};  // Último es meñique

String entrada = "";
int estadoActual[5] = {-1, -1, -1, -1, -1};  // Para evitar escribir repetido

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < 5; i++) {
    dedos[i].attach(pines[i]);
    dedos[i].write(0);
  }

  Serial.println("Asignación de pines:");
  Serial.println("Pulgar  → Pin 3");
  Serial.println("Índice  → Pin 5");
  Serial.println("Medio   → Pin 6");
  Serial.println("Anular  → Pin 9");
  Serial.println("Meñique → Pin 10");
  Serial.println("Esperando datos desde Python...");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      if (entrada.length() == 5) {
        for (int i = 0; i < 5; i++) {
          int nuevoEstado = entrada[i] - '0';
          if (nuevoEstado != estadoActual[i]) {
            estadoActual[i] = nuevoEstado;

            // Pulgar, Índice, Medio → lógica invertida
            if (i <= 2) {
              dedos[i].write(nuevoEstado == 1 ? 0 : maxAngulo[i]);
            } else {
              dedos[i].write(nuevoEstado == 1 ? maxAngulo[i] : 0);
            }
          }
        }
        Serial.print("Recibido: ");
        Serial.println(entrada);
      }
      entrada = "";
    } else {
      entrada += c;
    }
  }
}