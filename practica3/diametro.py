class Diametro:
    def __init__(self):
        """
        Un diccionario donde las llaves son direcciones de procesos y 
        los valores la distancia hasta ellos.
        """
        self.vecinos_inmediatos = {self: 0}
        """
        Al terminar la fase de vuelta, se van a recibir 'n' listas de rutas a
        todos los procesos alcanzables.
        'n' es igual al número de vecinos del presente proceso.
        Esta lista de rutas se puede convolucionar/colapsar para obtener las
        distancias mas cortas a todos los proceso alcanzables de la red.
        """
        self.listas_de_rutas = list()
        """
        Cuando se reciben mensajes de consulta de distancias por un vertice
        origen, vamos a recordar de que proceso obtuvimos esa petición.
        """
        self.referidos = {self: self}

    def fusionar_listas(lista_1, lista_2):
        return lista_1
        
    def start_diametro(self):
        self.log("Iniciando algoritmo para calcular la distancia a todos los procesos alcanzables.")
        self.mensajes_esperados = len(self.vecinos)
        for i in self.vecinos:
            self.vecinos_inmediatos[i] = 1
        self.log(f"Conocidos: {self.vecinos_inmediatos}.")
        self.log(f"Mandando go_consultar_diametro() a los vecinos.")
        for vecino in self.vecinos:
            vecino.msg("go_consultar_diametro", (self, self.vecinos_inmediatos.copy()), self)

    def go_consultar_diametro(self, origen, conocidos, remitente):
        procesos_a_revisar = set()
        for proceso in conocidos:
            procesos_a_revisar.add(proceso)
        self.log(f"Se ha recibido un mensaje de {remitente} con origen en {origen} para consultar sus distancias.")
        if (origen not in self.referidos) or (conocidos[remitente] < conocidos[self.referidos[origen]]):
            self.referidos[origen] = remitente
            self.log(f"Lista de referidos actualizada: {self.referidos}")
        else:
            self.log(f"Este proceso ya recibió antes un mensaje por parte de {self.referidos[origen]} preguntando por las distancias de {origen}.")
        self.log(f"Conocidos del origen ({origen}): {procesos_a_revisar}")
        self.log(f"Mis vecinos: {self.vecinos}")

        # Los procesos que el proceso que está haciendo la operación conoce, pero que aún no están en la lista recibida.
        diferencia_local = self.vecinos.difference(procesos_a_revisar)
        self.log(f"Diferencia local: {diferencia_local}")

        if len(diferencia_local) == 0:
            self.log(f"No hay procesos que aportar a la lista de distancias de {origen}, mandando back_consultar_diametro()")
            self.log(f"Lista final por devolver: {conocidos}")
            remitente.msg("back_consultar_diametro", (origen, conocidos), self)
        else:
            self.log(f"Este proceso conoce {len(diferencia_local)} que aún no está(n) en la lista de {origen} que recibió de {remitente}")
            distancia_de_los_procesos_a_referir = conocidos[self] + 1
            for proceso_por_aportar in diferencia_local:
                conocidos[proceso_por_aportar] = distancia_de_los_procesos_a_referir
            self.log(f"Se han añadido {diferencia_local} a la lista de {origen} con distancia {distancia_de_los_procesos_a_referir}")
            self.log(f"Lista actualizada: {conocidos}")
            self.log(f"Mandando go_consultar_diametro() con la lista actualizada de {origen} a {diferencia_local}")
            for vecino in diferencia_local:
                vecino.msg("go_consultar_diametro", (origen, conocidos.copy()), self)

    def back_consultar_diametro(self, origen, conocidos, remitente):
        if self is origen:
            self.listas_de_rutas.append(conocidos)
            self.mensajes_esperados -= 1
            self.log(f"Se ha recibido una lista de rutas, se siguen esperando {self.mensajes_esperados}")
            if self.mensajes_esperados <= 0:
                self.log("Se han recibido todas las listas de rutas esperadas")
                self.log(f"{self.listas_de_rutas}")
        else:
            self.log(f"Pasando back_consultar_diametro() con destino a {origen}")
            self.referidos[origen].msg("back_consultar_diametro", (origen, conocidos), self)
