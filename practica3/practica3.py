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
        self.dfs_children = set()
        self.dfs_parent = None

    def __repr__(self):
        return f"<{str(self.pid)}>"

    def start_dfs(self):
        if len(self.vecinos) <= 0:
            print(f"[RX] El nodo no tiene vecinos, no se puede ejecutar DFS")
            return
        print(f"[RX] DFS iniciado en {self}")
        self.dfs_parent = self
        print(f"[RX] {self.dfs_parent} es la raíz del árbol y su propio padre.")
        k = next(iter(self.vecinos))
        print(f"[RX] {k} ha sido selecionado como k de {self}")
        self.dfs_children.add(k)
        print(f"[RX] {k} ahora es hijo de {self}")
        visited = set()
        visited.add(self)
        print(f"[RX] Mandando GO({visited}, {self}) a {k}")
        k.go_dfs(visited, self)

    def go_dfs(self, visited: set, remitente):
        self.dfs_parent = remitente
        print(f"[RX] {self.dfs_parent} ahora es padre de {self}")
        print(f"[RX] Vecinos de {self}: {self.vecinos}, Visitados: {visited}")
        if self.vecinos.issubset(visited):
            print(f"[RX] El conjunto de vecinos de {self} es subconjunto del de visitados.")
            visited.add(self)
            print(f"[RX] Mandando BACK({visited}, {self}) y vaciando el conjunto de hijos.")
            remitente.back_dfs(visited, self)
            self.dfs_children = set()
        else:
            dif = self.vecinos.difference(visited)
            print(f"[RX] La diferencia de nodos entre visitados y vecinos de {self} es {dif}")
            k = next(iter(dif))
            print(f"[RX] {k} ha sido selecionado como k de {self}")
            visited.add(self)
            print(f"[RX] Nodos visitados hasta ahora: {visited}")
            k.go_dfs(visited, self)
            self.dfs_children.add(k)

    def back_dfs(self, visited: set, remitente):
        if self.vecinos.issubset(visited):
            if self.dfs_parent is self:
                print(f"[RX] DFS Completado en {self}.")
            else:
                print(f"[RX] El nodo {self} ha terminado de computar.")
                self.dfs_parent.back_dfs(visited, self)
        else:
            dif = self.vecinos.difference(visited)
            k = next(iter(dif))
            if k:
                visited.add(self)
                k.go_dfs(visited, self)
                self.dfs_children.add(k)


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


if __name__ == "__main__":
    args = parser.parse_args()
    grafica = construir_grafica(args.nodos)
    print(f"Se ha generado una red de nodos de grado {args.nodos} con las siguientes adyacencias:")
    for nodo in grafica:
        print(f"{grafica[nodo]}: {grafica[nodo].vecinos}")

    grafica[1].start_dfs()
    for nodo in grafica:
        print(f"Hijos de {grafica[nodo]}: {grafica[nodo].dfs_children}")