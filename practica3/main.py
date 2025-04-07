import argparse
import ast
import random
import simpy
import math
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
    grado = 0
    try:
        # Intentamos interpretar la entrada como una lista de aristas
        aristas = ast.literal_eval(f"[{args.procesos}]")
        grafica = generar_grafica_personalizada(aristas, env)
        grado = len(grafica)
    except (SyntaxError, ValueError, TypeError):
        # Si algo falla, intentamos interpretando la entrada como un entero
        grado = int(args.procesos)
        grafica = generar_grafica_aleatoria(grado, env)

    # Imprimir la red/gráfica
    print(f"Se ha generado la siguiente red con {len(grafica)} proceso(s):")
    for p in grafica:
        print(f"{grafica[p]}: {grafica[p].vecinos}")
    rondas_esperadas = math.ceil(grado * math.log(grado)) + 1
    print(f"Rondas esperadas: {rondas_esperadas}")

    # Inicializamos a todos los procesos de la red
    for p in grafica:
        grafica[p].start_distancias()
    # Iniciamos la simulación hasta las rondas esperadas en el peor caso.
    env.run(until=rondas_esperadas)
    # Una vez computadas las rondas esperadas, iniciamos el algoritmos DFS para recolectar candidatos al diámetro.
    print("\nIniciando fase de recolección de candidatos a diámetro")
    grafica[1].start_recolectar()
    # Reanudamos la simulación, no hace falta limitar las rondas porque DFS si reporta terminación.
    env.run()


if __name__ == "__main__":
    main()
