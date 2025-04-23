import argparse
import simpy
from collections import deque


class Proceso:
    def __init__(self, pid: int, env: simpy.core.Environment):
        self.pid = pid
        self.env = env
        self.vecino_izquierdo = None
        self.vecino_derecho = None
        self.continuar = True
        self.cola_mensajes_entrantes = deque()
        self.cola_mensajes_salientes = deque()
        self.mensajes_en_espera = deque()
        self.status = "ASLEEP"
        self.electo = "INDECISO"
        self.minimo = pid
        env.process(self.iterar())

    def __repr__(self):
        return f"<{self.pid}>"

    def __hash__(self):
        return hash(self.pid)

    def __eq__(self, other):
        if isinstance(other, Proceso):
            return self.pid == other.pid
        return NotImplemented

    """
    1. Leer los mensajes que hayan llegado en la ronda pasada y procesarlos.
    2. Hacer un número abitrario de operaciones computacionales hasta
    procesar todos los datos recibidos en los mensajes del paso anterior.
    3. Enviar mensajes si así se ha resuelto en el paso anterior, solo
    uno por vecino.
    """
    def iterar(self):
        while self.continuar:
            # Vaciamos en R los mensajes que vamos a procesar en esta ronda
            R = deque()
            for i in range(0, len(self.cola_mensajes_entrantes)):
                mensaje = self.cola_mensajes_entrantes.popleft()
                _, _, ronda_de_emision, _ = mensaje
                if ronda_de_emision != self.env.now:
                    R.append(mensaje)
            # Si el algoritmo aún no inicia, comenzamos a candidatearnos para lider
            if self.status == "ASLEEP":
                if len(R) == 0:
                    self.status = "PARTICIPATING"
                    self.minimo = self.pid
                    self.log(f"Estatus: {self.status} en la fase 1")
                    self.cola_mensajes_salientes.append((self.pid, 1, self.env.now))
                else:
                    self.status = "RELAY"
                    self.minimo = -1
            # Por defecto, si hay mensajes en R, los procesamos todos
            for i in range(0, len(R)):
                mensaje = R.popleft()
                origen, fase, ronda_de_emision, remitente = mensaje
                self.procesar_mensaje(origen, fase, ronda_de_emision)
            # Revisamos la lista de mensajes en espera
            for origen, fase, ronda_de_emision in self.mensajes_en_espera:
                delta = 2**(origen)-1
                self.log(f"El mensaje se recibió en la fase 2 ({ronda_de_emision}) hace {delta} rondas.")
                if ronda_de_emision >= delta:
                    self.log(f"Recirculando mensaje")
                    self.cola_mensajes_salientes.append((origen, fase, ronda_de_emision))
            # Enviamos o recirculamos los mensajes que hagan falta
            for origen, fase, ronda_de_emision in self.cola_mensajes_salientes:
                self.log(f"Enviando <{origen},{fase},{ronda_de_emision}> a {self.vecino_izquierdo}")
                self.vecino_izquierdo.msg(origen, fase, ronda_de_emision, self)

            yield self.env.timeout(1)  # Esperar a la siguiente ronda

    """
    Leer el contenido de un mensaje y tomar la decisión de nombrarse o no lider.

    Parameters
    ----------
    origen:
        ID del proceso donde se originó el mensaje.
    fase:
        Si el mensaje esta en su primer o segundo ciclo circulando en el anillo.
    ronda_de_emision:
        Ronda en la que se originó el mensaje.
    """
    def procesar_mensaje(self, origen: int, fase: int, ronda_de_emision: int):
        # Desestimamos el mensaje si el ID es mayor que el del proceso
        if origen > self.minimo:
            return
        # Si recibimos un ID menor, cambiamos estado de elección a NO LIDER
        elif origen < self.minimo:
            self.electo = "NO LIDER"
            self.continuar = False
            self.minimo = origen
            if self.status == "RELAY" and fase == 1:
                self.cola_mensajes_salientes.append((origen, fase, ronda_de_emision, self))
            else:
                self.mensajes_en_espera.append((origen, 2, self.env.now))
        elif origen == self.pid:
            self.electo = "LIDER"
            self.continuar = False
        self.log(f"Mensaje con origen en {origen} en la fase {fase} recibido. Nuevo estado: {self.electo}")

    """
    Recibimos un mensaje de algun vecino y los ponemos en la pila de mensajes
    esperando ser procesados.

    Parameters
    ----------
    origen:
        ID del proceso donde se originó el mensaje.
    fase:
        Si el mensaje esta en su primer o segundo ciclo circulando en el anillo.
    ronda_de_emision:
        Ronda en la que se originó el mensaje.
    remitente:
        Proceso que envía el mensaje.

    Returns
    -------
    bool:
        True si el mensaje fué recibido, False en otro caso.
    """
    def msg(self, origen: int, fase: int, ronda_de_emision: int, remitente):
        if remitente is self.vecino_izquierdo or remitente is self.vecino_derecho:
            mensaje = (origen, fase, ronda_de_emision, remitente)
            self.cola_mensajes_entrantes.append(mensaje)
            return True
        else:
            self.log(f"{remitente} ha intentado mandar un mensaje, pero no es vecino.")
            return False

    """
    Imprime un mensaje en pantalla con el prefijo de la ronda actual.

    Parameters
    ----------
    texto:
        Texto a imprimir en pantalla.
    """
    def log(self, texto):
        print(f"[Ronda {self.env.now} {self}] {texto}")


class Main:
    """
    Genera un número de procesos arbitrario y los conecta
    de modo pseudoaleatorio en una red/gráfica.

    Parameters
    ----------
    grado:
        Número de procesos a generar
    env:
        Entorno de SimPy al cual registrar cada proceso.

    Returns
    -------
    dict:
        Un diccionario donde las llaves son enteros y el
        contenido de cada una el objeto Proceso con el
        id de ese entero.
    """

    @staticmethod
    def generar_grafica(grado: int, env) -> dict:
        # Generamos el número de procesos especificado
        procesos = {i: Proceso(i, env) for i in range(1, grado + 1)}
        # Los unimos linealmente en un camino
        for i in range(2, grado):
            procesos[i].vecino_izquierdo = procesos[i - 1]
            procesos[i].vecino_derecho = procesos[i + 1]
        # Unimos los extremos del camino para hacer un anillo.
        procesos[grado].vecino_izquierdo = procesos[grado - 1]
        procesos[grado].vecino_derecho = procesos[1]
        procesos[1].vecino_izquierdo = procesos[grado]
        procesos[1].vecino_derecho = procesos[2]
        return procesos

    @staticmethod
    def ejecutar() -> Proceso:
        parser = argparse.ArgumentParser(prog="practica4", description="Practica 3")
        parser.add_argument(
            "procesos",
            type=int,
            help="Número de procesos de la red (al menos 3). Esta tendrá una topología de anillo.",
        )

        args = parser.parse_args()
        if args.procesos < 3:
            print("Error: Esta topología requiere de al menos 3 procesos.")
            return
        env = simpy.Environment()
        grado = args.procesos
        grafica = Main.generar_grafica(grado, env)

        # Imprimir la red/gráfica
        print(f"Se ha generado una red en forma de anillo con procesos del 1 al {grado}")

        for proceso in grafica:
            grafica[proceso].iterar()
        env.run()
        resultados = {proceso: proceso.electo for pid, proceso in grafica.items()}
        print(f"Resultados: {resultados}")
        for r in resultados:
            if resultados[r] == "LIDER":
                return r

if __name__ == "__main__":
    lider = Main.ejecutar()
    print(f"Lider seleccionado: {lider}")