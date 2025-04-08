import argparse
import ast
import random
import simpy
import math
from collections import deque

"""
En esta clase definimos los métodos necesarios para el algoritmo que calcula
el diámetro de la red. Todos los ejemplares de la clase proceso heredan sus
métodos particularmente.
"""
class Diametro:
    def __init__(self):
        # Trivialmente, cada proceso tiene distancia 0 a si mismo y 1 a sus vecinos
        self.vecinos_inmediatos = {self: 0}
        # Cada proceso recuerda cual lejos está cada proceso de la red
        self.distancias = {self: 0}
        # Una especie de libro de visitas para recordar la primera mención de cada proceso en uno en particular.
        self.referidos = {self: self}
        self.dfs_hijos = set()
        self.dfs_padre = None
        self.candidato_a_diametro = (0, self, self)

    def start_distancias(self):
        self.log("Iniciando algoritmo para calcular la distancia a todos los procesos alcanzables.")
        for i in self.vecinos:
            self.vecinos_inmediatos[i] = 1
        self.log(f"Conocidos: {self.vecinos_inmediatos}.")
        self.log(f"Mandando go_consultar_distancias() a los vecinos conocidos.")
        for vecino in self.vecinos:
            vecino.msg("go_consultar_distancias", (self, self.vecinos_inmediatos.copy()), self)

    def go_consultar_distancias(self, origen, conocidos, remitente):
        procesos_a_revisar = conocidos.copy()
        self.log(
            f"Se ha recibido un mensaje de {remitente} con origen en {origen} para consultar sus distancias."
        )
        self.log(f"Conocidos del origen ({origen}): {procesos_a_revisar}")
        self.log(f"Mis vecinos: {self.vecinos}")
        diferencia_local = self.vecinos.difference(procesos_a_revisar)
        self.log(f"Diferencia local: {diferencia_local}")

        if len(diferencia_local) == 0:
            self.log(
                f"No hay procesos que aportar a la lista de distancias de {origen}, mandando back_consultar_distancias()"
            )
            self.log(f"Lista final por devolver: {conocidos}")
            remitente.msg("back_consultar_distancias", (origen, conocidos), self)
        else:
            self.log(f"Este proceso conoce {len(diferencia_local)} que aún no está(n) en la lista de {origen} que recibió de {remitente}")
            distancia_de_los_procesos_a_referir = conocidos[self] + 1
            for proceso_por_aportar in diferencia_local:
                conocidos[proceso_por_aportar] = distancia_de_los_procesos_a_referir
            self.log(f"Se han añadido {diferencia_local} a la lista de {origen} con distancia {distancia_de_los_procesos_a_referir}")
            self.log(f"Lista actualizada: {conocidos}")
            if origen in self.referidos:
                self.log(f"Este proceso ya recibió antes un mensaje preguntando por las distancias de {origen}, mandando back_consultar_distancias()")
                remitente.msg("back_consultar_distancias", (origen, conocidos), self)
            else:
                self.referidos[origen] = remitente
                self.log(f"Lista de referidos actualizada: {self.referidos}")
                self.log(f"Mandando go_consultar_distancias() con la lista actualizada de {origen} a {diferencia_local}")
                for vecino in diferencia_local:
                    vecino.msg("go_consultar_distancias", (origen, conocidos.copy()), self)

    def back_consultar_distancias(self, origen, conocidos, remitente):
        if self is origen:
            self.log(f"Se ha recibido una lista de rutas nueva: {conocidos}")
            for key, value in conocidos.items():
                if key not in self.distancias or value < self.distancias[key]:
                    self.distancias[key] = value
            self.log(f"Lista de rutas local actualizada: {self.distancias}")
        else:
            self.log(f"Pasando back_consultar_distancias() desde {remitente} con destino a {origen}")
            self.referidos[origen].msg(
                "back_consultar_distancias", (origen, conocidos), self
            )

    def calcular_candidato_a_diametro(self):
        distancia_candidata = 0
        candidato = self
        for destino in self.distancias.keys():
            if self.distancias[destino] > distancia_candidata:
                candidato = destino
                distancia_candidata = self.distancias[destino]
        return (distancia_candidata, self, candidato)

    def start_recolectar(self):
        if len(self.vecinos) <= 0:
            self.log(f"El proceso no tiene vecinos, no se puede ejecutar DFS")
            return
        self.log(f"DFS para recolectar diametro iniciado en {self}")
        self.dfs_padre = self
        self.log(f"{self.dfs_padre} es la raíz del árbol y su propio padre.")
        proximo_destino = next(iter(self.vecinos))
        self.log(f"{proximo_destino} ha sido seleccionado como el siguiente destino.")
        self.dfs_hijos.add(proximo_destino)
        visited = set()
        visited.add(self)
        self.log(f"Mandando go_recolectar() a {proximo_destino}")
        proximo_destino.msg("go_recolectar", (visited, list()), self)

    def go_recolectar(self, visited, lista_de_diametros, remitente):
        self.dfs_padre = remitente
        self.log(f"Recibiendo una consulta de {remitente} para recolectar el diametro.")
        self.log(f"Vecinos: {self.vecinos}, Visitados: {visited}")
        # El Proceso es hoja
        if self.vecinos.issubset(visited):
            self.log(f"El conjunto de vecinos es subconjunto del de visitados.")
            visited.add(self)
            self.candidato_a_diametro = self.calcular_candidato_a_diametro()
            self.log(f"Candidato a diametro: {self.candidato_a_diametro}")
            lista_de_diametros.append(self.candidato_a_diametro)
            self.log(f"Mandando back_recolectar() y vaciando el conjunto de hijos.")
            self.log(f"{self} ha terminado de computar.")
            remitente.msg("back_recolectar", (visited, lista_de_diametros), self)
            self.dfs_hijos = set()
            self.continuar = False
        # El proceso no es hoja
        else:
            dif = self.vecinos.difference(visited)
            self.log(f"La diferencia de procesos entre visitados y vecinos es {dif}")
            proximo_destino = next(iter(dif))
            self.log(f"{proximo_destino} ha sido selecionado como siguiente destino a consultar")
            visited.add(self)
            self.log(f"Procesos visitados hasta ahora: {visited}")
            proximo_destino.msg("go_recolectar", (visited.copy(), lista_de_diametros), self)
            self.dfs_hijos.add(proximo_destino)

    def back_recolectar(self, visited, lista_de_diametros, remitente):
        # No quedan ramas por explorar
        if self.vecinos.issubset(visited):
            self.candidato_a_diametro = self.calcular_candidato_a_diametro()
            self.log(f"Candidato a diametro: {self.candidato_a_diametro}")
            lista_de_diametros.append(self.candidato_a_diametro)
            self.continuar = False
            # El proceso es raíz
            if self.dfs_padre is self:
                self.log(f"DFS de recolección completado con {len(lista_de_diametros)} candidatos.")
                # Como ya tenemos todos los candidatos, seleccionamos el máximo (diámetro)
                diametro = 0
                ganadores = list()
                for distancia, desde, hasta in lista_de_diametros:
                    if distancia > diametro:
                        diametro = distancia
                        ganadores = list()
                        ganadores.append((desde, hasta))
                    elif distancia == diametro:
                        ganadores.append((desde, hasta))
                self.log(f"El diámetro de la gráfica es {diametro}.")
                self.log(f"La(s) distancia(s) entre {ganadores} corresponden al diámetro (podrían no ser las únicas).")
            # El proceso no es raíz, seguir haciendo back
            else:
                self.dfs_padre.msg("back_recolectar", (visited, lista_de_diametros), self)
        # Quedan ramas por explorar
        else:
            dif = self.vecinos.difference(visited)
            self.log(f"Se ha compleado una de las ramas, faltan las de {dif}")
            proximo_destino = next(iter(dif))
            if proximo_destino:
                self.log(f"{proximo_destino} ha sido selecionado como siguiente destino a consultar")
                visited.add(self)
                proximo_destino.msg("go_recolectar", (visited, lista_de_diametros), self)
                self.dfs_hijos.add(proximo_destino)


"""
Esta clase define un proceso genérico que recibe, procesa e imprime mensajes
"""
class Proceso(Diametro):
    def __init__(self, pid: int, env: simpy.core.Environment):
        self.pid = pid
        self.env = env
        self.vecinos = set()
        self.continuar = True
        self.cola_mensajes = deque()
        env.process(self.iterar())
        Diametro.__init__(self)

    def __repr__(self):
        return f"<{self.pid}>"

    def __hash__(self):
        return hash(self.pid)

    def __eq__(self, other):
        if isinstance(other, Proceso):
            return self.pid == other.pid
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Proceso):
            return self.pid < other.pid
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Proceso):
            return self.pid <= other.pid
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Proceso):
            return self.pid > other.pid
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Proceso):
            return self.pid >= other.pid
        return NotImplemented

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
            # Leer los mensajes (uno por cada vecino)
            mensajes_por_vecino = {}
            for i in range(0, len(self.cola_mensajes)):
                mensaje = self.cola_mensajes.popleft()
                metodo, args, remitente, tiempo = mensaje
                if (remitente not in mensajes_por_vecino) and (tiempo != self.env.now):
                    mensajes_por_vecino[remitente] = (metodo, args, tiempo)
                else:
                    self.cola_mensajes.append(mensaje)

            # Procesar los mensajes recibidos
            for remitente, (metodo, args, tiempo) in mensajes_por_vecino.items():
                self.procesar_mensaje(metodo, args, remitente, tiempo)

            yield self.env.timeout(1)  # Esperar a la siguiente ronda

    """
    Agrega un mensaje a la cola de mensajes del proceso.
    Los mensajes se deberán de mandar en una tupla o un diccionario.

    Parameters
    ----------
    metodo:
        Nombre de la función/método que se desea invocar.
    args:
        Tupla/diccionario de argumentos.
    remitente:
        Proceso que envia el mensaje.
    """
    def msg(self, metodo: str, args, remitente):
        if remitente in self.vecinos | {self}:
            mensaje = (metodo, args, remitente, self.env.now)
            self.cola_mensajes.append(mensaje)
            return True
        else:
            self.log(f"{remitente} ha intentado mandar un mensaje, pero no es vecino.")
            return False

    """
    Procesa un mensaje llamando al método correspondiente si existe.
    """
    def procesar_mensaje(self, metodo, args, remitente, tiempo):
        if hasattr(self, metodo):  # Verifica si el proceso tiene el método
            metodo_a_llamar = getattr(self, metodo)
            if isinstance(args, dict):
                # Si los argumentos son un diccionario, usar **args
                args["remitente"] = remitente
                metodo_a_llamar(**args)
            elif isinstance(args, tuple):
                # Si son una tupla, pasarlos como argumentos
                metodo_a_llamar(*args, remitente)
            elif args is None:
                # Si no tiene argumentos, llamar al método tal cual
                metodo_a_llamar()
            else:
                # Si es un único argumento, pasarlo tal cual
                metodo_a_llamar(args)
        else:
            self.log(
                f"Recibiendo un mensaje para ejecutar {metodo}, pero no existe tal método."
            )

    """
    Imprime un mensaje en pantalla con el prefijo de la ronda actual.

    Parameters
    ----------
    texto:
        Texto a imprimir en pantalla.
    """
    def log(self, texto):
        print(f"[Ronda {self.env.now} {self}] {texto}")


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
    @staticmethod
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

    @staticmethod
    def ejecutar():
        parser = argparse.ArgumentParser(
            prog="practica3", description="Practica 3"
        )
        parser.add_argument(
            "procesos",
            type=str,
            help="Número de procesos a generar o lista de adyacencias de la forma '(u,v), (u,w), ...'",
        )

        args = parser.parse_args()
        env = simpy.Environment()
        grafica = dict()
        grado = 0
        try:
            # Intentamos interpretar la entrada como una lista de aristas
            aristas = ast.literal_eval(f"[{args.procesos}]")
            grafica = Main.generar_grafica_personalizada(aristas, env)
            grado = len(grafica)
        except (SyntaxError, ValueError, TypeError):
            # Si algo falla, intentamos interpretando la entrada como un entero
            grado = int(args.procesos)
            grafica = Main.generar_grafica_aleatoria(grado, env)

        # Imprimir la red/gráfica
        print(f"Se ha generado la siguiente red con {len(grafica)} proceso(s):")
        for p in grafica:
            print(f"{grafica[p]}: {grafica[p].vecinos}")
        rondas_esperadas = math.ceil(grado * math.log(grado)) + 1
        # Inicializamos a todos los procesos de la red
        for p in grafica:
            grafica[p].start_distancias()
        # Iniciamos la simulación hasta las rondas esperadas en el peor caso.
        print(f"Iniciando el algoritmo de cálculo de distancias para todos los vértices...")
        print(f"Rondas esperadas: {rondas_esperadas}")
        env.run(until=rondas_esperadas)
        # Una vez computadas las rondas esperadas, iniciamos el algoritmos DFS para recolectar candidatos al diámetro.
        print("Iniciando fase de recolección de candidatos a diámetro...")
        grafica[1].start_recolectar()
        # Reanudamos la simulación, no hace falta limitar las rondas porque DFS si reporta terminación.
        env.run()


if __name__ == "__main__":
    Main.ejecutar()
