import argparse
import simpy
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
        for i in range(2, grado):
            procesos[i].vecino_izquierdo = procesos[i - 1]
            procesos[i].vecino_derecho = procesos[i + 1]
        # Unimos los extremos del camino para hacer un anillo.
        procesos[grado].vecino_izquierdo = procesos[grado - 1]
        procesos[grado].vecino_derecho = procesos[1]
        procesos[1].vecino_izquierdo = procesos[grado]
        procesos[1].vecino_derecho = procesos[2]
        return procesos

    @staticmethod
    def ejecutar():
        parser = argparse.ArgumentParser(prog="practica4", description="Practica 3")
        parser.add_argument(
            "procesos",
            type=int,
            help="Número de procesos de la red (al menos 3). Esta tendrá una topología de anillo.",
        )

        args = parser.parse_args()
        if args.procesos < 3:
            print("Error: Esta topología requiere de al menos 3 procesos.")
            return
        env = simpy.Environment()
        grado = args.procesos
        grafica = Main.generar_grafica(grado, env)

        # Imprimir la red/gráfica
        print(f"Se ha generado una red en forma de anillo con procesos del 1 al {grado}")

        for proceso in grafica:
            grafica[proceso].iterar()
        env.run()
        
        resultados = {proceso: proceso.electo for pid, proceso in grafica.items()}
        print(f"Resultados: {resultados}")


if __name__ == "__main__":
    Main.ejecutar()
