// Definición de pines para los LEDs y las cargas
const int thumbLED = 13; // LED 1
const int indexLED = 12; // LED 2
const int middleLED =11; // LED 3
const int acPin = 10;    // Carga AC
const int dcPin = 9;    // Carga DC

/*const int thumbLED = 32; // LED 1
const int indexLED = 33; // LED 2
const int middleLED =4; // LED 3
const int acPin = 27;    // Carga AC
const int dcPin = 14;    // Carga DC*/

// Variables para mantener el estado anterior de cada dispositivo
int estadoAnteriorThumb = 0;
int estadoAnteriorIndex = 0;
int estadoAnteriorMiddle = 0;
int estadoAnteriorAC = 0;
int estadoAnteriorDC = 0;

// Variables para controlar si los dispositivos ya se han activado una vez
bool movidoThumb = false;
bool movidoIndex = false;
bool movidoMiddle = false;
bool movidoAC = false;
bool movidoDC = false;

void setup() {
  Serial.begin(9600);
  
  // Configura los pines de los LEDs y las cargas como salidas
  pinMode(thumbLED, OUTPUT);
  pinMode(indexLED, OUTPUT);
  pinMode(middleLED, OUTPUT);
  pinMode(acPin, OUTPUT);
  pinMode(dcPin, OUTPUT);

  // pinMode(34, OUTPUT);
  // pinMode(35, OUTPUT);
  // pinMode(36, OUTPUT);
  // pinMode(27, OUTPUT);
  // pinMode(14, OUTPUT);

}

void loop() {
  if (Serial.available() >= 5) {
    char buffer[6];
    Serial.readBytes(buffer, 6); // Lee 5 bytes (uno para cada dispositivo y un byte extra para el final de línea)
    buffer[5] = '\0'; // Agrega un carácter nulo al final del buffer para convertirlo en una cadena
    Serial.print(Serial.readBytes(buffer, 6));
    
    // Convierte el buffer a valores enteros para cada dispositivo
    int thumb = buffer[0] - '0';
    int index = buffer[1] - '0';
    int middle = buffer[2] - '0';
    int acState = buffer[3] - '0';
    int dcState = buffer[4] - '0';

    // Controla los LEDs y las cargas en función de las señales
    controlarDispositivo(thumb, thumbLED, estadoAnteriorThumb, movidoThumb);
    controlarDispositivo(index, indexLED, estadoAnteriorIndex, movidoIndex);
    controlarDispositivo(middle, middleLED, estadoAnteriorMiddle, movidoMiddle);
    controlarDispositivo(acState, acPin, estadoAnteriorAC, movidoAC);
    controlarDispositivo(dcState, dcPin, estadoAnteriorDC, movidoDC);

    // Actualiza los estados anteriores de cada dispositivo
    estadoAnteriorThumb = thumb;
    estadoAnteriorIndex = index;
    estadoAnteriorMiddle = middle;
    estadoAnteriorAC = acState;
    estadoAnteriorDC = dcState;
  }
}

// Función para controlar los LEDs y las cargas
void controlarDispositivo(int estado, int pin, int &estadoAnterior, bool &movido) {
  if (estado != estadoAnterior) {
    if (estado == 1 && !movido) {
      digitalWrite(pin, HIGH); // Enciende el LED o la carga si el estado es 1 y no se ha activado antes
      movido = true;           // Marca que el dispositivo ya ha sido activado una vez
    } else if (estado == 0) {
      digitalWrite(pin, LOW);  // Apaga el LED o la carga si el estado es 0
      movido = false;          // Reinicia el marcador de activación
    }
    // Actualiza el estado anterior del dispositivo
    estadoAnterior = estado;
  }
}
