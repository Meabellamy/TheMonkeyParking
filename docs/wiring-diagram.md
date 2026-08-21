# Diagrama de conexiones (Arduino Uno + Mini Protoboard)

Este proyecto usa **una sola pluma (servo)** compartida para entrada y
salida, con **2 sensores infrarrojos** ubicados a cada lado de esa misma
pluma.

## Idea general

```
                         PLUMA (1 servo)
                              |
   AFUERA  ----[IR Entrada]---||---[IR Salida]----  ADENTRO
   (autos que quieren entrar)     (autos que quieren salir)
```

- El sensor de **entrada** ve pasar autos que quieren entrar.
- El sensor de **salida** ve pasar autos que quieren salir.
- Los dos sensores y el servo comparten los mismos rieles de alimentación
  en la mini protoboard, así el Arduino solo necesita entregar un cable
  de 5V y un cable de GND hacia la protoboard.

## Por qué usamos la protoboard así

El Arduino Uno tiene pocos pines de 5V/GND libres. En vez de conectar 3
cables de VCC y 3 de GND directo a la placa (queda desordenado y se
pueden aflojar), armamos dos "rieles" en la protoboard:

- **Riel (+)**: alimentado por un solo cable desde el pin `5V` del Arduino.
- **Riel (–)**: alimentado por un solo cable desde el pin `GND` del Arduino.

Desde esos rieles, con jumpers cortos, alimentamos el servo y los 2
sensores IR. Solo los cables de **señal/datos** van directo a los pines
digitales del Arduino.

## Tabla de conexiones

| Componente              | Cable                | Va a                          |
|--------------------------|-----------------------|--------------------------------|
| Arduino `5V`             | 1x macho-macho        | Riel (+) de la protoboard      |
| Arduino `GND`            | 1x macho-macho        | Riel (–) de la protoboard      |
| Servo — cable rojo (VCC) | jumper corto          | Riel (+) de la protoboard      |
| Servo — cable marrón/negro (GND) | jumper corto   | Riel (–) de la protoboard      |
| Servo — cable naranja/amarillo (señal) | macho-hembra | Arduino pin **D9**       |
| Sensor IR Entrada — VCC  | jumper corto          | Riel (+) de la protoboard      |
| Sensor IR Entrada — GND  | jumper corto          | Riel (–) de la protoboard      |
| Sensor IR Entrada — OUT  | macho-hembra          | Arduino pin **D2**             |
| Sensor IR Salida — VCC   | jumper corto          | Riel (+) de la protoboard      |
| Sensor IR Salida — GND   | jumper corto          | Riel (–) de la protoboard      |
| Sensor IR Salida — OUT   | macho-hembra          | Arduino pin **D3**             |

> Los pines D2 y D3 se eligieron porque son las entradas de interrupción
> del Uno; si en el futuro querés hacerlo más avanzado (usando
> interrupciones en vez de leer todo el tiempo en `loop()`), ya están
> listos para eso. Con el firmware actual funcionan igual que cualquier
> pin digital.

## Resumen visual de pines usados en el Arduino

```
                +-----------------------+
                |       ARDUINO UNO     |
                |                       |
   IR Entrada --| D2                    |
   IR Salida  --| D3                    |
   Servo señal--| D9 (PWM)              |
                |                       |
                | 5V  ---> riel (+) protoboard
                | GND ---> riel (-) protoboard
                +-----------------------+
```

## Notas importantes

1. **Polaridad del servo**: normalmente el cable naranja/amarillo es la
   señal, el rojo es VCC (+5V) y el marrón/negro es GND. Revisa el
   datasheet de tu servo específico si tiene otros colores.
2. **Consumo de corriente**: al usar un solo servo, el consumo es mucho
   menor que con dos. Igualmente, si notás que el Arduino se reinicia
   solo al mover el servo, alimentá el riel (+) de la protoboard con una
   fuente externa de 5V (pilas/cargador USB) en vez del pin 5V del
   Arduino, y unir los GND de ambas fuentes.
3. **Sensores IR activo en bajo/alto**: la mayoría de los módulos IR
   tipo FC-51 devuelven `LOW` cuando detectan un obstáculo. El firmware
   ya está configurado así (`SENSOR_ACTIVO_EN_BAJO = true`). Si tu
   sensor detecta al revés (la pluma reacciona sin autos, o no
   reacciona con autos), cambiá esa variable a `false` en
   `firmware/parking_barrier.ino`.
