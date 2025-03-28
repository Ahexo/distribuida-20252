class Diametro:
    def __init__(self):
        self.bfs_padre = None
        self.bfs_distancia = float("inf")
        self.bfs_vecinos_esperados = self.vecinos.copy()

    def start_diametro(self):
        print(f"[Ronda {self.env.now}] Iniciando el cálculo del diámetro desde {self}")
        self.bfs_padre = self
        self.bfs_distancia = 0
        self.bfs_vecinos_esperados = self.vecinos.copy()
        print(
            f"[Ronda {self.env.now}] {self} espera mensajes de {self.bfs_vecinos_esperados}"
        )
        for vecino in self.vecinos:
            vecino.msg("bfs_diametro", (self, 1), self)

    def bfs_diametro(self, origen, distancia, remitente):
        if len(self.bfs_vecinos_esperados) == 0:
            self.bfs_vecinos_esperados = self.vecinos.copy()
        if distancia < self.bfs_distancia:
            print(
                f"[Ronda {self.env.now}] {self} recibió BFS desde {remitente} con una mejor distancia ({distancia})"
            )
            self.bfs_padre = remitente
            self.bfs_distancia = distancia
            for vecino in self.vecinos - {
                remitente
            }:  # Evita devolver el mensaje al padre
                vecino.msg("bfs_diametro", (origen, distancia + 1), self)
        elif distancia == self.bfs_distancia and remitente.pid < self.bfs_padre.pid:
            # En caso de empate, elegir el nodo con menor ID como padre
            self.bfs_padre = remitente
        else:
            print(
                f"[Ronda {self.env.now}] {self} recibió BFS desde {remitente} con distancia {distancia}, pero {self} ya tiene una mejor ({self.bfs_distancia}, {self.bfs_padre})"
            )

        self.bfs_vecinos_esperados.discard(remitente)
        print(
            f"[Ronda {self.env.now}] {self} sigue esperando mensajes de {self.bfs_vecinos_esperados}"
        )

        if len(list(self.bfs_vecinos_esperados)) == 0:
            self.reportar_diametro()

    def reportar_diametro(self):
        """
        Cada nodo reporta su distancia, el que tenga la mayor será la primera etapa del diámetro.
        """
        print(f"[Ronda {self.env.now}] {self} reporta distancia {self.bfs_distancia}")
        if self.bfs_distancia == max(n.bfs_distancia for n in self.vecinos):
            print(
                f"[Ronda {self.env.now}] {self} es el nodo más lejano en la primera fase de BFS"
            )
            self.start_diametro_segundo_bfs()

    def start_diametro_segundo_bfs(self):
        """
        Se ejecuta el segundo BFS desde el nodo más lejano encontrado en el primer BFS.
        """
        print(
            f"[Ronda {self.env.now}] Iniciando segunda fase del cálculo del diámetro desde {self}"
        )
        self.bfs_padre = self
        self.bfs_distancia = 0
        for vecino in self.vecinos:
            vecino.msg("bfs_diametro_final", (self, 1), self)

    def bfs_diametro_final(self, origen, distancia, remitente):
        """
        Segunda fase del BFS para encontrar el diámetro.
        """
        if distancia < self.bfs_distancia:
            self.bfs_padre = remitente
            self.bfs_distancia = distancia
            for vecino in self.vecinos - {remitente}:
                vecino.msg("bfs_diametro_final", (origen, distancia + 1), self)
        elif distancia == self.bfs_distancia and remitente.pid < self.bfs_padre.pid:
            self.bfs_padre = remitente

    def reportar_diametro_final(self):
        """
        Reporta la mayor distancia alcanzada en la segunda fase.
        """
        print(
            f"[Ronda {self.env.now}] {self} reporta distancia final {self.bfs_distancia}"
        )
        if self.bfs_distancia == max(n.bfs_distancia for n in self.vecinos):
            print(
                f"[Ronda {self.env.now}] El diámetro de la red es {self.bfs_distancia}"
            )
