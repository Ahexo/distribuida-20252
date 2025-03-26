import simpy
import argparse
import random
from collections import deque
from DFS import DFS

parser = argparse.ArgumentParser(
    prog="practica3",
    description="Un programa para simular la red de un sistema distribuido y hallar el diámetro de su gráfica subyacente.",
    epilog="Implementado por Axel Rodríguez y José David Aguilar para el curso de Computación Distribuida 7106 2025-2.",
)

parser.add_argument(
    "nodos",
    type=int,
    default=8,
    help="Número de nodos que tendrá el sistema distribuido",
)


class Nodo(DFS):
    def __init__(self, pid: int, env):
        self.pid = pid
        self.env = env
        self.vecinos = set()
        self.action = env.process(self.iterar())
        self.continuar = True
        self.cola_mensajes = deque()
        DFS.__init__(self)

    def __repr__(self):
        return f"<{self.pid}>"

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
            print(f"[Ronda {self.env.now}] {self} está iterando.")

            # Leer los mensajes (uno por cada vecino)
            mensajes_por_vecino = {}
            for i in range(0, len(self.cola_mensajes)):
                mensaje = self.cola_mensajes.popleft()
                metodo, args, remitente, tiempo = mensaje
                if (remitente not in mensajes_por_vecino) and (
                    tiempo is not self.env.now
                ):
                    mensajes_por_vecino[remitente] = (metodo, args, tiempo)
                else:
                    self.cola_mensajes.append(mensaje)

            # Procesar los mensajes recibidos
            for remitente, (metodo, args, tiempo) in mensajes_por_vecino.items():
                self.procesar_mensaje(metodo, args, remitente, tiempo)

            yield self.env.timeout(1)  # Esperar a la siguiente ronda

    """
    Agrega un mensaje a la cola de mensajes del nodo.
    Los mensajes se deberán de mandar en una tupla o un diccionario.
    """

    def msg(self, metodo: str, args, remitente):
        mensaje = (metodo, args, remitente, self.env.now)
        self.cola_mensajes.append(mensaje)

    """
    Procesa un mensaje llamando al método correspondiente si existe.
    """

    def procesar_mensaje(self, metodo, args, remitente, tiempo):
        if hasattr(self, metodo):  # Verifica si el nodo tiene el método
            metodo_a_llamar = getattr(self, metodo)
            if isinstance(args, dict):
                # Si los argumentos son un diccionario, usar **args
                args["remitente"] = remitente
                metodo_a_llamar(**args)
            elif isinstance(args, tuple):
                # Si son una tupla, pasarlos como argumentos
                metodo_a_llamar(*args, remitente)
            else:
                # Si es un único argumento, pasarlo tal cual
                metodo_a_llamar(args)
        else:
            print(
                f"{self} recibió un mensaje para {metodo}, pero no existe tal método."
            )

    def ejemplo(self, dato, remitente):
        print(
            f"[Ronda {self.env.now}] {self} ejecuta 'ejemplo' desde {remitente} con dato={dato}"
        )
        destinatario = random.choice(list(self.vecinos))
        numero_misterioso = random.randint(0, 1000)
        print(
            f"[Ronda {self.env.now}] {self} está enviando (ejemplo, {numero_misterioso}) a {destinatario}"
        )
        destinatario.msg("ejemplo", (numero_misterioso,), self)


"""
    Genera el número de nodos (que son objetos de la clase nodo) que se
    especifica como argumento y los une en una gŕafica.

    En un principio, todos los nodos estarán unidos linealmente en un solo
    camino. Posteriormente, para todo par de vértices en la gráfica, se
    agregará un vértice que los una con probabilidad del 50%.

    Parameters
    ----------
    grado: int
        Número de nodos/vertices de la gráfica.

    Returns
    -------
    dict:
        Diccionario de la forma {pid: nodo}
"""


def construir_grafica(grado: int, env):
    # Generamos el número de nodos especificado
    nodos = {i: Nodo(i, env) for i in range(1, grado + 1)}
    # Los unimos linealmente
    for i in range(1, grado):
        nodos[i].vecinos.add(nodos[i + 1])
        nodos[i + 1].vecinos.add(nodos[i])
    # Añadimos aristas con probabilidad del 50% para todo par de nodos.
    for i in range(1, grado + 1):
        for j in range(i + 1, grado + 1):
            if random.random() < 0.5:
                nodos[i].vecinos.add(nodos[j])
                nodos[j].vecinos.add(nodos[i])
    return nodos


if __name__ == "__main__":
    args = parser.parse_args()
    env = simpy.Environment()
    grafica = construir_grafica(args.nodos, env)
    print(
        f"Se ha generado una red de nodos de grado {args.nodos} con las siguientes adyacencias:"
    )
    for nodo in grafica:
        print(f"{grafica[nodo]}: {grafica[nodo].vecinos}")

    grafica[1].start_dfs()
    env.run()

    print("DFS completado:")
    for nodo in grafica:
        print(f"{grafica[nodo]}: {grafica[nodo].dfs_children}")
