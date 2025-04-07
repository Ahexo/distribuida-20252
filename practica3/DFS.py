class DFS:
    def __init__(self):
        self.dfs_children = set()
        self.dfs_parent = None

    def start_dfs(self):
        if len(self.vecinos) <= 0:
            self.log(f"El nodo no tiene vecinos, no se puede ejecutar DFS")
            return
        self.log(f"DFS iniciado en {self}")
        self.dfs_parent = self
        self.log(f"{self.dfs_parent} es la raíz del árbol y su propio padre.")
        k = next(iter(self.vecinos))
        self.log(f"{k} ha sido seleccionado como k (destinatario) de {self}")
        self.dfs_children.add(k)
        self.log(f"{self} ha añadido a {k} a su lista de hijos.")
        visited = set()
        visited.add(self)
        self.log(f"Mandando go_dfs({visited}, {self}) a {k}")
        k.msg("go_dfs", (visited,), self)

    def go_dfs(self, visited: set, remitente):
        self.dfs_parent = remitente
        self.log(f"{self} ahora reconoce a {self.dfs_parent} como su padre.")
        self.log(f"Vecinos de {self}: {self.vecinos}, Visitados: {visited}")
        if self.vecinos.issubset(visited):
            self.log(f"El conjunto de vecinos de {self} es subconjunto del de visitados.")
            visited.add(self)
            self.log(f"Mandando BACK({visited}, {self}) y vaciando el conjunto de hijos.")
            self.log(f"{self} ha terminado de computar.")
            remitente.msg("back_dfs", (visited,), self)
            self.dfs_children = set()
            self.continuar = False
        else:
            dif = self.vecinos.difference(visited)
            self.log(f"La diferencia de nodos entre visitados y vecinos de {self} es {dif}")
            k = next(iter(dif))
            self.log(f"{k} ha sido selecionado como k de {self}")
            visited.add(self)
            self.log(f"Nodos visitados hasta ahora: {visited}")
            k.msg("go_dfs", (visited,), self)
            self.dfs_children.add(k)

    def back_dfs(self, visited: set, remitente):
        if self.vecinos.issubset(visited):
            self.continuar = False
            if self.dfs_parent is self:
                self.log(f"DFS Completado, la raíz es {self}.")
            else:
                self.log(f"El nodo {self} ha terminado de computar.")
                self.dfs_parent.msg("back_dfs", (visited,), self)
        else:
            dif = self.vecinos.difference(visited)
            k = next(iter(dif))
            if k:
                visited.add(self)
                k.msg("go_dfs", (visited,), self)
                self.dfs_children.add(k)
