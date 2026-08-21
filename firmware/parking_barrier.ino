/*
  The Monkey Parking - Firmware Arduino Uno
  ---------------------------------------------------
  Controla una UNICA pluma (servo) compartida para entrada y salida,
  usando 2 sensores infrarrojos (uno de cada lado de la pluma).

  - Lleva la cuenta de plazas ocupadas/disponibles.
  - Bloquea automaticamente la entrada cuando el estacionamiento esta lleno.
  - Libera la entrada automaticamente en cuanto sale un auto.
  - Reporta el estado por Serial (USB) para que la app de Python
    dibuje el layout visual y el contador digital en tiempo real.

  Protocolo Serial (Arduino -> PC), una linea de texto por mensaje:
    STATE,<ocupados>,<capacidad>,<gate>,<lleno>
      ocupados  -> cantidad de autos adentro
      capacidad -> capacidad maxima configurada (CAPACIDAD_MAXIMA)
      gate      -> 0 = pluma cerrada, 1 = pluma abierta
      lleno     -> 0 = hay lugar, 1 = estacionamiento lleno

  Protocolo Serial (PC -> Arduino), comandos de texto simples:
    RESET   -> reinicia el contador de ocupados a 0 (util para pruebas)
*/

#include <Servo.h>

// ---------------------- CONFIGURACION ----------------------

const int CAPACIDAD_MAXIMA = 5;      // Cantidad de plazas del estacionamiento

const int PIN_SERVO = 9;             // Pin PWM del servo de la pluma
const int PIN_IR_ENTRADA = 2;        // Sensor IR lado de afuera de la pluma
const int PIN_IR_SALIDA = 3;         // Sensor IR lado de adentro de la pluma

// La mayoria de los modulos IR (tipo FC-51) dan LOW cuando detectan un
// objeto. Si el tuyo funciona al reves, cambia esto a false.
const bool SENSOR_ACTIVO_EN_BAJO = true;

const int ANGULO_CERRADO = 0;        // Angulo de la pluma cerrada
const int ANGULO_ABIERTO = 90;       // Angulo de la pluma abierta

const unsigned long TIEMPO_ESPERA_PASO_MS = 4000; // Maximo que espera a que el auto libere el sensor
const unsigned long RETARDO_CIERRE_MS = 600;       // Colchon extra antes de cerrar la pluma
const unsigned long INTERVALO_ESTADO_MS = 1000;    // Cada cuanto se re-envia el estado aunque no cambie

// -------------------------------------------------------------

Servo pluma;
int ocupados = 0;
unsigned long ultimoEnvioEstado = 0;

bool sensorDetecta(int pin) {
  int lectura = digitalRead(pin);
  return SENSOR_ACTIVO_EN_BAJO ? (lectura == LOW) : (lectura == HIGH);
}

void abrirPluma() {
  pluma.write(ANGULO_ABIERTO);
}

void cerrarPluma() {
  pluma.write(ANGULO_CERRADO);
}

bool plumaAbierta() {
  return pluma.read() > (ANGULO_CERRADO + ANGULO_ABIERTO) / 2;
}

void enviarEstado() {
  bool lleno = (ocupados >= CAPACIDAD_MAXIMA);
  Serial.print("STATE,");
  Serial.print(ocupados);
  Serial.print(",");
  Serial.print(CAPACIDAD_MAXIMA);
  Serial.print(",");
  Serial.print(plumaAbierta() ? 1 : 0);
  Serial.print(",");
  Serial.println(lleno ? 1 : 0);
}

// Abre la pluma, espera a que el sensor indicado deje de detectar el auto
// (o hasta que se cumpla el timeout), agrega un colchon y cierra.
void procesarPaso(int pinSensor) {
  abrirPluma();
  enviarEstado();

  unsigned long inicio = millis();
  while (sensorDetecta(pinSensor) && (millis() - inicio) < TIEMPO_ESPERA_PASO_MS) {
    delay(50);
  }
  // Espera un poco mas por si el auto todavia no libero del todo el sensor
  delay(RETARDO_CIERRE_MS);

  cerrarPluma();
  enviarEstado();
}

void manejarComandoSerial() {
  if (Serial.available() == 0) return;

  String comando = Serial.readStringUntil('\n');
  comando.trim();
  if (comando.equalsIgnoreCase("RESET")) {
    ocupados = 0;
    enviarEstado();
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(PIN_IR_ENTRADA, INPUT);
  pinMode(PIN_IR_SALIDA, INPUT);

  pluma.attach(PIN_SERVO);
  cerrarPluma();

  enviarEstado();
}

void loop() {
  manejarComandoSerial();

  bool hayAutoEntrando = sensorDetecta(PIN_IR_ENTRADA);
  bool hayAutoSaliendo = sensorDetecta(PIN_IR_SALIDA);

  // La salida siempre tiene prioridad y nunca se bloquea.
  if (hayAutoSaliendo) {
    procesarPaso(PIN_IR_SALIDA);
    if (ocupados > 0) {
      ocupados--;
    }
    enviarEstado();
  } else if (hayAutoEntrando) {
    if (ocupados < CAPACIDAD_MAXIMA) {
      procesarPaso(PIN_IR_ENTRADA);
      ocupados++;
      enviarEstado();
    }
    // Si esta lleno, no se hace nada: la pluma permanece cerrada.
  }

  // Reporte periodico de estado (por si la PC se conecta despues de un evento).
  if (millis() - ultimoEnvioEstado >= INTERVALO_ESTADO_MS) {
    enviarEstado();
    ultimoEnvioEstado = millis();
  }
}
