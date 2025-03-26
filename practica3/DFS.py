class DFS:
    def __init__(self):
        self.dfs_children = set()
        self.dfs_parent = None

    def start_dfs(self):
        if len(self.vecinos) <= 0:
            print(
                f"[Ronda {self.env.now}] El nodo no tiene vecinos, no se puede ejecutar DFS"
            )
            return
        print(f"[Ronda {self.env.now}] DFS iniciado en {self}")
        self.dfs_parent = self
        print(
            f"[Ronda {self.env.now}] {self.dfs_parent} es la raíz del árbol y su propio padre."
        )
        k = next(iter(self.vecinos))
        print(
            f"[Ronda {self.env.now}] {k} ha sido seleccionado como k (destinatario) de {self}"
        )
        self.dfs_children.add(k)
        print(f"[Ronda {self.env.now}] {k} ahora es hijo de {self}")
        visited = set()
        visited.add(self)
        print(f"[Ronda {self.env.now}] Mandando GO({visited}, {self}) a {k}")
        k.msg("go_dfs", (visited,), self)

    def go_dfs(self, visited: set, remitente):
        self.dfs_parent = remitente
        print(f"[Ronda {self.env.now}] {self.dfs_parent} ahora es padre de {self}")
        print(
            f"[Ronda {self.env.now}] Vecinos de {self}: {self.vecinos}, Visitados: {visited}"
        )
        if self.vecinos.issubset(visited):
            print(
                f"[Ronda {self.env.now}] El conjunto de vecinos de {self} es subconjunto del de visitados."
            )
            visited.add(self)
            print(
                f"[Ronda {self.env.now}] Mandando BACK({visited}, {self}) y vaciando el conjunto de hijos."
            )
            remitente.msg("back_dfs", (visited,), self)
            self.dfs_children = set()
        else:
            dif = self.vecinos.difference(visited)
            print(
                f"[Ronda {self.env.now}] La diferencia de nodos entre visitados y vecinos de {self} es {dif}"
            )
            k = next(iter(dif))
            print(f"[Ronda {self.env.now}] {k} ha sido selecionado como k de {self}")
            visited.add(self)
            print(f"[Ronda {self.env.now}] Nodos visitados hasta ahora: {visited}")
            k.msg("go_dfs", (visited,), self)
            self.dfs_children.add(k)

    def back_dfs(self, visited: set, remitente):
        if self.vecinos.issubset(visited):
            self.continuar = False
            if self.dfs_parent is self:
                print(f"[Ronda {self.env.now}] DFS Completado, la raíz es {self}.")
            else:
                print(
                    f"[Ronda {self.env.now}] El nodo {self} ha terminado de computar."
                )
                self.dfs_parent.msg("back_dfs", (visited,), self)
        else:
            dif = self.vecinos.difference(visited)
            k = next(iter(dif))
            if k:
                visited.add(self)
                k.msg("go_dfs", (visited,), self)
                self.dfs_children.add(k)
