import argparse
import random
import simpy

parser = argparse.ArgumentParser(
                    prog="practica3",
                    description="Un programa para simular la red de un sistema distribuido y hallar el diámetro de su gráfica subyacente.",
                    epilog="Implementado por Axel Rodríguez y José David Aguilar para el curso de Computación Distribuida 7106 2025-2.")

parser.add_argument("nodos",
                    type=int,
                    default=8,
                    help="Número de nodos que tendrá el sistema distribuido")


class Nodo:
    def __init__(self, pid: int, env=None):
        self.pid = pid
        self.vecinos = set()
        self.dfs_children = set()
        self.dfs_parent = None
        self.bfs_children = set()
        self.bfs_parent = None
        self.bfs_level = float('inf')
        self.expected_msg = float('inf')

    def __repr__(self):
        return f"<{str(self.pid)}>"

    def start_bfs(self):
        print(f"[RX BFS] BFS iniciado en {self}")
        self.go_bfs(-1, self)

    def refresh_bfs(self, distancia: int, remitente):
        self.bfs_parent = remitente
        self.bfs_children = set()
        self.bfs_level = distancia + 1
        self.expected_msg = len(self.vecinos)
        if remitente in self.vecinos:
            self.expected_msg -= 1
        print(f"[RX BFS] {self}: Padre: {self.bfs_parent}, Hijos: {self.bfs_children}, Nivel: {self.bfs_level}, ExpMsg: {self.expected_msg}")

    def go_bfs(self, distancia: int, remitente):
        if self.bfs_parent is None:
            print(f"[RX BFS] {self} no tiene padre, acepta la oferta de {remitente}")
            self.refresh_bfs(distancia, remitente)
            if self.expected_msg == 0:
                print(f"[RX BFS] {self} no tiene más vecinos a los que mandar mensajes, mandando BACK(Yes, {self.bfs_level}) al padre {self.bfs_parent}")
                self.bfs_parent.back_bfs(True, distancia + 1, self)
            else:
                destinatarios = self.vecinos.copy()
                destinatarios.discard(remitente)
                print(f"[RX BFS] {self} está enviando mensajes GO({self.bfs_level}) a sus vecinos: {destinatarios}")
                for k in destinatarios:
                    k.go_bfs(distancia + 1, self)
        elif self.bfs_level > distancia + 1:
            print(f"[RX BFS] {self} ha encontrado que si es hijo de {remitente} su nivel mejorará de {self.bfs_level} a {distancia + 1}, así que se va a cambiar.")
            self.refresh_bfs(distancia, remitente)
            if self.expected_msg == 0:
                print(f"[RX BFS] {self} no tiene más vecinos a los que mandar mensajes, mandando BACK(Yes, {self.bfs_level}) al padre {self.bfs_parent}")
                self.bfs_parent.back_bfs(True, self.bfs_level, self)
            else:
                destinatarios = self.vecinos.copy()
                destinatarios.remove(remitente)
                print(f"[RX BFS] {self} está enviando mensajes GO({self.bfs_level}) a sus vecinos: {destinatarios}")
                for k in destinatarios:
                    k.go_bfs(distancia + 1, self)
        else:
            print(f"[RX BFS] {self} (nivel {self.bfs_level}) ha recibido una oferta de paternidad de {remitente} a {distancia + 1}, pero su nivel no mejoraría.")
            print(f"[RX BFS] {self} mandando BACK(No, {self.bfs_level}) a {remitente}")
            remitente.back_bfs(False, distancia + 1, self)

    def back_bfs(self, cambiar_padre: bool, distancia: int, remitente):
        print(f"[RX BFS] {self} recibió un mensaje BACK de {remitente} con estado ({cambiar_padre}, {distancia})")
        print(f"[RX BFS] Distancia recibida de {remitente}: {distancia}. Nivel de {self}: {self.bfs_level}; ")
        if distancia == self.bfs_level + 1:
            self.expected_msg -= 1
            if cambiar_padre is True:
                self.bfs_children.add(remitente)
                print(f"[RX BFS] {remitente} ha sido anexado en la lista de hijos de {self}")
                # self.expected_msg -= 1
                print(f"[RX BFS] {self}: Padre: {self.bfs_parent}, Hijos: {self.bfs_children}, Nivel: {self.bfs_level}, ExpMsg: {self.expected_msg}")
                if self.expected_msg <= 0:
                    if self.bfs_parent is self:
                        print(f"[RX BFS] BFS Completado en {self}.")
                    else:
                        print(f"[RX BFS] El nodo {self} ha terminado de computar. Mandando BACK(Yes, {self.bfs_level}) a su padre {self.bfs_parent}.")
        else:
            print(f"{self} está enterado de que {remitente} rechazó su oferta de paternidad")

        print(f"[RX BFS] {self} ahora espera {self.expected_msg} mensajes")


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
def construir_grafica(grado: int):
    # Generamos el número de nodos especificado
    nodos = {i: Nodo(i) for i in range(1, grado + 1)}
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


def bfs(grafica):
    grafica[1].start_bfs()
    for nodo in grafica:
        print(f"Mensajes esperados por {grafica[nodo]}: {grafica[nodo].expected_msg}")
        print(f"Hijos de {grafica[nodo]}: {grafica[nodo].bfs_children}")


if __name__ == "__main__":
    args = parser.parse_args()
    grafica = construir_grafica(args.nodos)
    print(f"Se ha generado una red de nodos de grado {args.nodos} con las siguientes adyacencias:")
    for nodo in grafica:
        print(f"{grafica[nodo]}: {grafica[nodo].vecinos}")

    ambiente = simpy.Environment()
    bfs(grafica)