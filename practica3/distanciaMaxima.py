class DistanciaMaxima:
    def __init__(self):
        self.max_distancia = -1
        self.max_nodo = None
        self.mensajes_esperados = float("inf")
        self.mensajes_recibidos = 0
        self.terminado = False

    def start_distancia_maxima(self):
        """Inicia la propagación del BFS desde este nodo."""
        print(
            f"[Ronda {self.env.now}] Iniciando cálculo de distancia máxima desde {self}"
        )
        self.max_distancia = 0
        self.max_nodo = self
        self.mensajes_esperados = len(self.vecinos)

        for vecino in self.vecinos:
            vecino.msg("bfs_distancia_max", (0, self), self)

    def bfs_distancia_max(self, distancia, origen, remitente):
        """Procesa un mensaje BFS y propaga la búsqueda si es necesario."""
        if self.mensajes_esperados == float("inf"):
            self.mensajes_esperados = len(self.vecinos)

        self.mensajes_recibidos += 1
        nueva_distancia = distancia + 1

        if nueva_distancia > self.max_distancia:
            print(
                f"[Ronda {self.env.now}] {self} tiene nueva distancia máxima: {nueva_distancia} desde {remitente}"
            )
            self.max_distancia = nueva_distancia
            self.max_nodo = origen

            for vecino in self.vecinos - {remitente}:
                vecino.msg("bfs_distancia_max", (nueva_distancia, origen), self)
        else:
            print(
                f"[Ronda {self.env.now}] {self}(distanciaMax={self.max_distancia}) recibió una distancia depreciable {nueva_distancia} desde {remitente}."
            )

        print(
            f"[Ronda {self.env.now}] {self} ha recibido {self.mensajes_recibidos}/{self.mensajes_esperados} mensajes."
        )

        # Si ya recibimos todos los mensajes esperados, terminamos
        if self.mensajes_recibidos >= self.mensajes_esperados:
            self.finalizar_proceso()

    def finalizar_proceso(self):
        """Marca el nodo como terminado y notifica a los vecinos si es necesario."""
        if not self.terminado:
            print(
                f"[Ronda {self.env.now}] {self} ha recibido todos los mensajes esperados y termina con distanciaMax={self.max_distancia}."
            )
            self.terminado = True

        # Opcional: enviar mensaje de terminación a otros nodos
        # for vecino in self.vecinos:
        # vecino.msg("terminado", (self.max_distancia, self), self)

    def terminado(self, distanciaMax, remitente):
        """Recibe notificación de que otro nodo terminó."""
        print(
            f"[Ronda {self.env.now}] {self} ha recibido un mensaje de terminación de {remitente}, cuya distancia máxima es {distanciaMax}."
        )
