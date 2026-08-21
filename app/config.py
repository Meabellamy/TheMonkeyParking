"""
Configuracion de la app de escritorio de The Monkey Parking.

Edita estos valores segun tu entorno. No hace falta tocar nada mas
del proyecto para adaptarlo a otra PC.
"""

# Puerto serie donde esta conectado el Arduino.
# Dejalo en "AUTO" para que la app intente detectarlo sola.
# Si falla la auto-deteccion, poné el puerto exacto, por ejemplo:
#   Windows:      "COM3"
#   Mac/Linux:    "/dev/ttyUSB0" o "/dev/cu.usbmodem14101"
SERIAL_PORT = "AUTO"

# Debe coincidir con el Serial.begin(...) del firmware (parking_barrier.ino).
BAUD_RATE = 9600

# Capacidad que se muestra ANTES de recibir el primer mensaje del Arduino.
# Una vez conectado, el valor real (CAPACIDAD_MAXIMA del firmware) manda.
CAPACIDAD_INICIAL = 5

# Tamano de la ventana de la app.
ANCHO_VENTANA = 900
ALTO_VENTANA = 600
