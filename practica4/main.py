import argparse
import ast
import random
import simpy
import math
from proceso import Proceso


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
        for i in range(1, grado):
            procesos[i].vecinos.add(procesos[i + 1])
            procesos[i + 1].vecinos.add(procesos[i])
        # Unimos los extremos del camino para hacer un anillo.
        procesos[grado].vecinos.add(procesos[1])
        procesos[1].vecinos.add(procesos[grado])
        return procesos

    @staticmethod
    def ejecutar():
        parser = argparse.ArgumentParser(
            prog="practica4", description="Practica 3"
        )
        parser.add_argument(
            "procesos",
            type=int,
            help="Número de procesos de la red (al menos 3). Esta tendrá una topología de anillo.",
        )

        args = parser.parse_args()
        if args.procesos < 3:
            print("Error: The number of processes must be at least 3.")
            return
        env = simpy.Environment()
        grado = args.procesos
        grafica = Main.generar_grafica(grado, env)

        # Imprimir la red/gráfica
        print(f"Se ha generado la siguiente red con {len(grafica)} proceso(s):")
        for p in grafica:
            print(f"{grafica[p]}: {grafica[p].vecinos}")
        rondas_esperadas = math.ceil(grado * math.log(grado)) + 1


if __name__ == "__main__":
    Main.ejecutar()
