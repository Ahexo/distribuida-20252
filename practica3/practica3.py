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

    def __repr__(self):
        return f"<{str(self.pid)}>"

    def go(self, remitente):
        pass

    def back(self, remitente):
        pass


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