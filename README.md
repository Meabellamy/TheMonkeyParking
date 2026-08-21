# 🐒🅿️ The Monkey Parking (Arduino + Python)

Maqueta a escala de un estacionamiento con **pluma automática**, **conteo
de plazas disponibles**, **bloqueo automático de entrada cuando está
lleno** y un **layout visual en la laptop** que se actualiza en tiempo
real según lo que hace el Arduino.

## Índice

- [Cómo funciona](#cómo-funciona)
- [Materiales necesarios](#materiales-necesarios)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Paso 1: Armado físico](#paso-1-armado-físico)
- [Paso 2: Instalar Arduino IDE y subir el firmware](#paso-2-instalar-arduino-ide-y-subir-el-firmware)
- [Paso 3: Instalar Python y la app visual](#paso-3-instalar-python-y-la-app-visual)
- [Paso 4: Ejecutar todo junto](#paso-4-ejecutar-todo-junto)
- [Cómo cambiar la capacidad del estacionamiento](#cómo-cambiar-la-capacidad-del-estacionamiento)
- [Solución de problemas](#solución-de-problemas)

## Cómo funciona

- Hay **una sola pluma** (un servo) que se comparte para la entrada y la
  salida, como una barrera real de un solo carril.
- Hay **2 sensores infrarrojos**, uno de cada lado de la pluma: uno
  detecta autos que quieren **entrar** y el otro autos que quieren
  **salir**.
- El Arduino lleva la cuenta de cuántos autos hay adentro (`ocupados`) y
  la compara contra una capacidad máxima configurable.
  - Si hay lugar y un auto llega a la entrada → **se abre la pluma**, el
    auto pasa, se cierra, y sube el contador de ocupados.
  - Si **no hay lugar** → la pluma **no se abre** para autos que quieren
    entrar (la salida nunca se bloquea).
  - Si un auto sale → se abre la pluma, pasa, se cierra, y baja el
    contador. Si el estacionamiento estaba lleno, automáticamente vuelve
    a permitir la entrada.
- El Arduino manda todo este estado por el cable USB (puerto serie) a la
  laptop.
- Una app de Python (con Pygame) dibuja el estacionamiento: plazas
  ocupadas/libres, el número de **plazas disponibles en grande**, el
  estado de la pluma, y un aviso de "LLENO" cuando corresponde.

## Materiales necesarios

- 1x placa Arduino Uno
- 2x sensores infrarrojos (IR) para Arduino
- 1x servo motor de 180° (con suficiente torque para mover la pluma)
- 1x mini protoboard
- Cables macho-macho y macho-hembra
- Base de cartón para montar la maqueta
- Materiales estéticos a elección (para decorar la maqueta)
- Una laptop con un puerto USB

## Estructura del proyecto

```
TheMonkeyParking/
├── README.md                    <- este archivo
├── firmware/
│   └── parking_barrier.ino      <- codigo que va DENTRO del Arduino
├── app/
│   ├── main.py                  <- app visual (Pygame)
│   ├── serial_reader.py         <- lectura del puerto serie
│   ├── config.py                <- configuracion (puerto, tamano ventana)
│   └── requirements.txt         <- dependencias de Python
└── docs/
    └── wiring-diagram.md        <- diagrama detallado de conexiones
```

## Paso 1: Armado físico

1. Fijá el servo en un extremo de la base de cartón, en el lugar donde
   va a estar la barrera única de entrada/salida.
2. Colocá un sensor IR apuntando hacia el lado de **afuera** de la pluma
   (detecta autos que quieren entrar) y el otro apuntando hacia el lado
   de **adentro** (detecta autos que quieren salir).
3. Armá los rieles de alimentación en la mini protoboard y conectá todo
   siguiendo la tabla y el diagrama detallado en
   [`docs/wiring-diagram.md`](docs/wiring-diagram.md). En resumen:
   - Servo → señal a pin **D9**, alimentación por la protoboard.
   - Sensor IR entrada → señal a pin **D2**, alimentación por la protoboard.
   - Sensor IR salida → señal a pin **D3**, alimentación por la protoboard.
4. Decorá la maqueta con los materiales estéticos, marcando los cajones
   de estacionamiento (la cantidad de cajones dibujados debe coincidir
   con la `CAPACIDAD_MAXIMA` del firmware, ver más abajo).

## Paso 2: Instalar Arduino IDE y subir el firmware

1. Descargá e instalá el **Arduino IDE** (gratis) desde
   [arduino.cc/en/software](https://www.arduino.cc/en/software).
2. Conectá el Arduino Uno a la laptop con el cable USB.
3. Abrí el Arduino IDE y abrí el archivo
   `firmware/parking_barrier.ino` de este proyecto (`Archivo → Abrir`).
4. En el menú `Herramientas`:
   - `Placa` → seleccioná **Arduino Uno**.
   - `Puerto` → seleccioná el puerto donde aparece tu Arduino (en
     Windows suele ser algo como `COM3`, `COM4`, etc.).
5. La primera vez, instalá la librería **Servo** si no aparece ya
   incluida: `Herramientas → Gestionar Bibliotecas...` → buscar
   "Servo" → Instalar (viene incluida de fábrica en la mayoría de las
   instalaciones, así que puede que ya la tengas).
6. Hacé clic en el botón **Subir** (flecha hacia la derecha). Esperá a
   que diga "Subida completada".
7. Con el Monitor Serie (`Herramientas → Monitor Serie`, velocidad
   `9600 baudios`) podés ver mensajes como:
   ```
   STATE,0,5,0,0
   ```
   Esto confirma que el Arduino ya está funcionando solo (0 ocupados de
   5, pluma cerrada, no lleno). Cerrá el Monitor Serie antes de pasar al
   siguiente paso (solo un programa a la vez puede usar el puerto).

## Paso 3: Instalar Python y la app visual

1. Descargá e instalá **Python** (versión 3.9 o superior) desde
   [python.org/downloads](https://www.python.org/downloads/). En
   Windows, asegurate de tildar la casilla **"Add Python to PATH"**
   durante la instalación.
2. Abrí una terminal (PowerShell en Windows, Terminal en Mac/Linux) y
   navegá hasta la carpeta `app` de este proyecto:
   ```bash
   cd ruta/al/proyecto/app
   ```
3. Instalá las dependencias con un solo comando:
   ```bash
   pip install -r requirements.txt
   ```
   > Esto instala `pyserial` (para hablar con el Arduino) y `pygame-ce`
   > (para dibujar la interfaz). Se usa `pygame-ce` en vez de `pygame`
   > porque tiene instaladores listos para usar en versiones recientes
   > de Python, evitando errores de compilación.

## Paso 4: Ejecutar todo junto

1. Conectá el Arduino por USB (si no lo estaba ya) y asegurate de que
   **no** tengas abierto el Monitor Serie del Arduino IDE ni ningún
   otro programa usando ese puerto.
2. Dentro de la carpeta `app`, ejecutá:
   ```bash
   python main.py
   ```
3. Se abre una ventana mostrando el estacionamiento. Abajo de todo vas a
   ver el estado de la conexión:
   - `Conectado en COM3` (o similar) → todo bien.
   - `Buscando Arduino...` → todavía no encontró el puerto (esperá unos
     segundos, la app reintenta sola).
4. Probá pasando la mano/un objeto por cada sensor IR: deberías ver la
   pluma abrirse en la maqueta física, el contador de plazas
   actualizarse en pantalla, y el cartel de "LLENO" aparecer cuando se
   alcanza la capacidad máxima.

### Si la app no encuentra el puerto solo

Abrí `app/config.py` y cambiá:

```python
SERIAL_PORT = "AUTO"
```

por el puerto exacto que viste en el Arduino IDE, por ejemplo:

```python
SERIAL_PORT = "COM3"          # Windows
# o
SERIAL_PORT = "/dev/ttyUSB0"  # Linux
# o
SERIAL_PORT = "/dev/cu.usbmodem14101"  # Mac
```

## Cómo cambiar la capacidad del estacionamiento

Editá esta línea en `firmware/parking_barrier.ino`:

```cpp
const int CAPACIDAD_MAXIMA = 5;
```

Cambiá el `5` por la cantidad de cajones que tenga tu maqueta, volvé a
subir el sketch (Paso 2.6), y listo — la app de Python toma ese valor
automáticamente del Arduino, no hace falta tocar nada en Python.

## Solución de problemas

| Problema | Posible causa / solución |
|---|---|
| El servo no se mueve | Revisá que el cable de señal esté en D9 y que la alimentación del servo esté bien conectada a los rieles de la protoboard. |
| El servo tiembla o el Arduino se reinicia al moverse | Falta de corriente. Alimentá el servo desde una fuente externa de 5V (compartiendo GND con el Arduino) en vez del pin 5V del Uno. |
| Un sensor no detecta nada / detecta todo el tiempo | Puede estar invertida la lógica del sensor. Cambiá `SENSOR_ACTIVO_EN_BAJO` a `false` en el `.ino` y volvé a subir. |
| La app de Python dice "Buscando Arduino..." para siempre | Verificá que no haya otro programa (como el Monitor Serie) usando el puerto, y que el puerto en `config.py` sea el correcto. |
| Error al instalar `pygame` | Usá `pygame-ce` (ya está en `requirements.txt`), que trae instaladores listos para versiones nuevas de Python. |
| La pluma no bloquea la entrada estando lleno | Confirmá que `CAPACIDAD_MAXIMA` en el `.ino` coincida con la cantidad real de cajones, y que el sketch actualizado ya esté subido al Arduino. |
