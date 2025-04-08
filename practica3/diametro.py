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