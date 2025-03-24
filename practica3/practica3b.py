import argparse
import random

parser = argparse.ArgumentParser(
                    prog="practica3",
                    description="Un programa para simular la red de un sistema distribuido y hallar el diámetro de su gráfica subyacente.",
                    epilog="Implementado por Axel Rodríguez y José David Aguilar para el curso de Computación Distribuida 7106 2025-2.")

parser.add_argument("nodos",
                    type=int,
                    default=8,
                    help="Número de nodos que tendrá el sistema distribuido")

class nodo:
    def __init__(self, pid: int):
        self.pid = pid
        self.vecinos = set()
        self.bfs_children = set()
        self.bfs_parent = None
        self.bfs_level = float('inf')
        self.expected_msg = 0

    def __repr__(self):
        return f"<{str(self.pid)}>"

    def start_bfs(self):
        print(f"[RX BFS] BFS iniciado en {self}")
        self.go_bfs(-1, self)

    def refresh_bfs(self, distancia: int, remitente):
        self.bfs_parent = remitente
        self.bfs_children = set()
        self.bfs_level = distancia + 1
        self.expected_msg = len(self.vecinos - {remitente})

    def go_bfs(self, distancia: int, remitente):
        if self.bfs_parent is None:
            print(f"[RX BFS] {self} no tiene padre, acepta la oferta de {remitente}")
            self.refresh_bfs(distancia, remitente)
            print(f"[RX BFS] {self}: Padre: {self.bfs_parent}, Hijos: {self.bfs_children}, Nivel: {self.bfs_level}, ExpMsg: {self.expected_msg}")
            if self.expected_msg == 0:
                print(f"[RX BFS] {self} no tiene más vecinos a los que mandar mensajes, enviando BACK(True, {self.bfs_level}) a {self.bfs_parent}")
                self.bfs_parent.back_bfs(True, self.bfs_level, self)
            else:
                destinatarios = self.vecinos - {remitente}
                print(f"[RX BFS] {self} enviando GO({self.bfs_level}) a {destinatarios}")
                for k in destinatarios:
                    k.go_bfs(distancia + 1, self)

        elif self.bfs_level > distancia + 1:
            print(f"[RX BFS] {self} cambia su padre a {remitente} para mejorar nivel a {distancia + 1}")
            self.refresh_bfs(distancia, remitente)
            print(f"[RX BFS] {self}: Padre: {self.bfs_parent}, Hijos: {self.bfs_children}, Nivel: {self.bfs_level}, ExpMsg: {self.expected_msg}")
            if self.expected_msg == 0:
                print(f"[RX BFS] {self} no tiene más vecinos a los que mandar mensajes, enviando BACK(True, {self.bfs_level}) a {self.bfs_parent}")
                self.bfs_parent.back_bfs(True, self.bfs_level, self)
            else:
                destinatarios = self.vecinos - {remitente}
                print(f"[RX BFS] {self} enviando GO({self.bfs_level}) a {destinatarios}")
                for k in destinatarios:
                    k.go_bfs(distancia + 1, self)

        else:
            print(f"[RX BFS] {self} rechaza oferta de {remitente}, enviando BACK(False, {distancia + 1})")
            remitente.back_bfs(False, distancia + 1, self)

    def back_bfs(self, cambiar_padre: bool, distancia: int, remitente):
        print(f"[RX BFS] {self} recibió BACK de {remitente} ({cambiar_padre}, {distancia})")
        if distancia == self.bfs_level + 1:
            self.expected_msg -= 1

            if cambiar_padre:
                self.bfs_children.add(remitente)  # ✅ Now we ONLY add confirmed children
            else:
                self.bfs_children.discard(remitente)  # ✅ Remove incorrect children

            if self.expected_msg == 0:
                if self.bfs_parent is self:
                    print(f"[RX BFS] BFS completado en {self}.")
                else:
                    final_state = bool(self.bfs_children)  # True if it has children
                    print(f"[RX BFS] {self} ha terminado. Enviando BACK({final_state}, {self.bfs_level}) a {self.bfs_parent}")
                    self.bfs_parent.back_bfs(final_state, self.bfs_level, self)


def construir_grafica(grado: int):
    # Generamos el número de nodos especificado
    nodos = {i: nodo(i) for i in range(1, grado + 1)}
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

    bfs(grafica)