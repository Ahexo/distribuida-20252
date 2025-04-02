import simpy
import random
from collections import deque
from diametro import Diametro


class Proceso(Diametro):
    def __init__(self, pid: int, env: simpy.core.Environment):
        self.pid = pid
        self.env = env
        self.vecinos = set()
        self.action = env.process(self.iterar())
        self.continuar = True
        self.cola_mensajes = deque()
        Diametro.__init__(self)

    def __repr__(self):
        return f"\033[1;30m<{self.pid}>\033[0m"

    def __hash__(self):
        return hash(self.pid)

    def __eq__(self, other):
        if isinstance(other, Proceso):
            return self.pid == other.pid
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Proceso):
            return self.pid < other.pid
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Proceso):
            return self.pid <= other.pid
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Proceso):
            return self.pid > other.pid
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Proceso):
            return self.pid >= other.pid
        return NotImplemented

    """
    1. Leer los mensajes que hayan llegado en la ronda pasada, solo uno
    por vecino.
    2. Hacer un número abitrario de operaciones computacionales hasta
    procesar todos los datos recibidos en los mensajes del paso anterior.
    3. Enviar mensajes si así se ha resuelto en el paso anterior, solo
    uno por vecino.
    """

    def iterar(self):
        while self.continuar:
            self.log("Iterando...")

            # Leer los mensajes (uno por cada vecino)
            mensajes_por_vecino = {}
            for i in range(0, len(self.cola_mensajes)):
                mensaje = self.cola_mensajes.popleft()
                metodo, args, remitente, tiempo = mensaje
                if (remitente not in mensajes_por_vecino) and (tiempo != self.env.now):
                    mensajes_por_vecino[remitente] = (metodo, args, tiempo)
                else:
                    self.cola_mensajes.append(mensaje)

            # Procesar los mensajes recibidos
            for remitente, (metodo, args, tiempo) in mensajes_por_vecino.items():
                self.procesar_mensaje(metodo, args, remitente, tiempo)

            yield self.env.timeout(1)  # Esperar a la siguiente ronda

    """
    Agrega un mensaje a la cola de mensajes del proceso.
    Los mensajes se deberán de mandar en una tupla o un diccionario.
    """

    def msg(self, metodo: str, args, remitente):
        if remitente in self.vecinos | {self}:
            mensaje = (metodo, args, remitente, self.env.now)
            self.cola_mensajes.append(mensaje)
        else:
            self.log(f"{remitente} ha intentado mandar un mensaje, pero no es vecino.")

    """
    Procesa un mensaje llamando al método correspondiente si existe.
    """

    def procesar_mensaje(self, metodo, args, remitente, tiempo):
        if hasattr(self, metodo):  # Verifica si el proceso tiene el método
            metodo_a_llamar = getattr(self, metodo)
            if isinstance(args, dict):
                # Si los argumentos son un diccionario, usar **args
                args["remitente"] = remitente
                metodo_a_llamar(**args)
            elif isinstance(args, tuple):
                # Si son una tupla, pasarlos como argumentos
                metodo_a_llamar(*args, remitente)
            elif args is None:
                # Si no tiene argumentos, llamar al método tal cual
                metodo_a_llamar()
            else:
                # Si es un único argumento, pasarlo tal cual
                metodo_a_llamar(args)
        else:
            self.log(
                f"Recibiendo un mensaje para ejecutar {metodo}, pero no existe tal método."
            )

    """
    Imprime un mensaje en pantalla con el prefijo de la ronda actual.

    Parameters
    ----------
    texto:
        Texto a imprimir en pantalla.
    """

    def log(self, texto):
        print(f"[Ronda {self.env.now} {self}] {texto}")

    """
    Recibir un mensaje e imprimirlo.

    Parameters
    ----------
    dato:
        Mensaje.
    remitente:
        Proceso que manda el mensaje.
    """

    def echo(self, dato, remitente):
        self.log(f"{remitente} dice: {dato}")
        destinatario = random.choice(list(self.vecinos))
        numero_misterioso = random.randint(0, 1000)
        self.log(f"Enviando (echo, {numero_misterioso}) a {destinatario}")
        destinatario.msg("echo", (numero_misterioso,), self)
