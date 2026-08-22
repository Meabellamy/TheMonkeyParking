"""
Manejo de la conexion serie con el Arduino.

Corre en un hilo aparte para no trabar el dibujo de la interfaz (Tkinter)
mientras se espera texto por el puerto serie.
"""

import threading
import time

import serial
from serial.tools import list_ports

import config


class EstadoEstacionamiento:
    """Ultimo estado conocido, compartido entre el hilo serie y la UI."""

    def __init__(self):
        self.lock = threading.Lock()
        self.ocupados = 0
        self.capacidad = config.CAPACIDAD_INICIAL
        self.pluma_abierta = False
        self.lleno = False
        self.conectado = False
        self.puerto = None
        self.ultimo_error = None

    def actualizar_desde_linea(self, linea: str) -> bool:
        """Parsea una linea 'STATE,ocupados,capacidad,gate,lleno'.

        Devuelve True si la linea tenia el formato esperado.
        """
        partes = linea.strip().split(",")
        if len(partes) != 5 or partes[0] != "STATE":
            return False

        try:
            ocupados = int(partes[1])
            capacidad = int(partes[2])
            gate = int(partes[3])
            lleno = int(partes[4])
        except ValueError:
            return False

        with self.lock:
            self.ocupados = ocupados
            self.capacidad = capacidad
            self.pluma_abierta = bool(gate)
            self.lleno = bool(lleno)
        return True

    def snapshot(self):
        """Copia segura del estado actual para dibujar en la UI."""
        with self.lock:
            return {
                "ocupados": self.ocupados,
                "capacidad": self.capacidad,
                "pluma_abierta": self.pluma_abierta,
                "lleno": self.lleno,
                "conectado": self.conectado,
                "puerto": self.puerto,
                "ultimo_error": self.ultimo_error,
            }


def detectar_puerto_arduino():
    """Busca automaticamente un puerto serie que parezca un Arduino."""
    candidatos = list(list_ports.comports())

    palabras_clave = ("arduino", "usb-serial", "usb serial", "ch340", "wch")
    for puerto in candidatos:
        descripcion = f"{puerto.description} {puerto.manufacturer or ''}".lower()
        if any(palabra in descripcion for palabra in palabras_clave):
            return puerto.device

    # Si no encontro nada obvio, devuelve el primer puerto disponible (si hay).
    if candidatos:
        return candidatos[0].device

    return None


class LectorSerial(threading.Thread):
    """Hilo que mantiene la conexion serie viva y actualiza el estado."""

    def __init__(self, estado: EstadoEstacionamiento):
        super().__init__(daemon=True)
        self.estado = estado
        self._detener = threading.Event()

    def run(self):
        while not self._detener.is_set():
            puerto = config.SERIAL_PORT
            if puerto == "AUTO":
                puerto = detectar_puerto_arduino()

            if not puerto:
                with self.estado.lock:
                    self.estado.conectado = False
                    self.estado.ultimo_error = "No se encontro ningun puerto serie."
                time.sleep(2)
                continue

            try:
                with serial.Serial(puerto, config.BAUD_RATE, timeout=1) as conexion:
                    with self.estado.lock:
                        self.estado.conectado = True
                        self.estado.puerto = puerto
                        self.estado.ultimo_error = None

                    # El Arduino se resetea al abrir el puerto; le damos
                    # un momento antes de leer datos utiles.
                    time.sleep(2)

                    while not self._detener.is_set():
                        try:
                            linea = conexion.readline().decode("utf-8", errors="ignore")
                        except serial.SerialException:
                            break

                        if linea:
                            self.estado.actualizar_desde_linea(linea)

            except serial.SerialException as error:
                with self.estado.lock:
                    self.estado.conectado = False
                    self.estado.ultimo_error = str(error)
                time.sleep(2)

    def detener(self):
        self._detener.set()
