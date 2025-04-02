import argparse
import ast
import random
import simpy
from proceso import Proceso

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


def generar_grafica_aleatoria(grado: int, env) -> dict:
    # Generamos el número de procesos especificado
    procesos = {i: Proceso(i, env) for i in range(1, grado + 1)}
    # Los unimos linealmente
    for i in range(1, grado):
        procesos[i].vecinos.add(procesos[i + 1])
        procesos[i + 1].vecinos.add(procesos[i])
    # Añadimos aristas con probabilidad del 50% para todo par de procesos.
    for i in range(1, grado + 1):
        for j in range(i + 1, grado + 1):
            if random.random() < 0.5:
                procesos[i].vecinos.add(procesos[j])
                procesos[j].vecinos.add(procesos[i])
    return procesos


"""
    Construye una red/gráfica de procesos a partir de una lista de
    tuplas (aristas) que la induce.

    Parameters
    ----------
    aristas:
        Lista de tuplas (aristas).
    env:
        Entorno de SimPy al cual registrar cada proceso.

    Returns
    -------
    dict:
        Un diccionario donde las llaves son enteros y el
        contenido de cada una el objeto Proceso con el
        id de ese entero.
"""


def generar_grafica_personalizada(aristas: list, env) -> dict:
    procesos = dict()
    for arista in aristas:
        u, v = arista
        if u not in procesos:
            procesos[u] = Proceso(u, env)
        if v not in procesos:
            procesos[v] = Proceso(v, env)
        procesos[u].vecinos.add(procesos[v])
        procesos[v].vecinos.add(procesos[u])
    return procesos


def main():
    parser = argparse.ArgumentParser(
        prog="comdist", description="A program to generate graphs."
    )
    parser.add_argument(
        "procesos",
        type=str,
        help="Número de procesos a generar o lista de adyacencias de la forma '(u,v), (u,w), ...'",
    )
    parser.add_argument(
        "-l",
        "--lider",
        nargs="?",
        help="Proceso lider por el cual se va a iniciar el programa.",
    )

    args = parser.parse_args()
    if args.lider:
        print(f"Lider indicado: {args.lider} ({type(args.lider)})")
    env = simpy.Environment()
    grafica = dict()
    try:
        # Intentamos interpretar la entrada como una lista de aristas
        aristas = ast.literal_eval(f"[{args.procesos}]")
        grafica = generar_grafica_personalizada(aristas, env)
    except (SyntaxError, ValueError, TypeError):
        # Si algo falla, intentamos interpretando la entrada como un entero
        num_vertices = int(args.procesos)
        grafica = generar_grafica_aleatoria(num_vertices, env)

    # Imprimir la red/gráfica
    print(f"Se ha generado la siguiente red con {len(grafica)} proceso(s):")
    for i in grafica:
        print(f"{grafica[i]}: {grafica[i].vecinos}")

    # Probar
    lider = grafica[1]
    lider.start_diametro()
    # lider.msg("start_diametro", None, lider)
    env.run(until=9)

    # when env.now >= n*2
    # lider.recolectar_maximos()


if __name__ == "__main__":
    main()
