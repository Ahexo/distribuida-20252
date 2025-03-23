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

"""
    Genera una lista de tuplas que abstraen a los vértices de una gráfica
    simple con un grado en particular.

    En un principio, todos los nodos estarán unidos linealmente en un solo
    camino. Posteriormente, para todo par de vértices en la gráfica, se
    agregará un vértice que los una con probabilidad del 50%.

    Parameters
    ----------
    grado: int
        Número de nodos/vertices de la gráfica.

    Returns
    -------
    list:
        Una lista de tuplas (aristas) de la gráfica.
    """
def generar_grafica(grado: int):
    vertices = set()
    for i in range(1, grado):
        vertices.add((i, i + 1))
    for i in range(1, grado + 1):
        for j in range(i + 1, grado + 1):
            if random.random() < 0.5:
                vertices.add((i, j))
    return sorted(list(vertices))


if __name__ == "__main__":
    args = parser.parse_args()
    print(args.nodos)
    vertices = generar_grafica(args.nodos)
    print(vertices)
    print(len(vertices))