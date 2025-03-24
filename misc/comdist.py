import simpy

"""
Todos los procesos ejecutan una iteración por ronda, donde cada iteración
se divide en tres fases:
Fase 1: Recepción. El proceso tiene una estructura de datos a modo de buzón
        donde lee a lo más un mensaje de cada uno de sus vecinos y carga
        los datos que reciba en estos.
Fase 2: Computación. Ejecuta una cantidad arbitraria de operaciones
        con los datos que recibieron en la fase anterior. También puede
        que no haga nada.
Fase 3: Expulsión. El proceso envia a lo mucho un mensaje a cada uno de sus
        vecinos.
"""
class Proceso:
    def __init__(self, pid: int, env: simpy.core.Environment):
        self.env = env
        self.pid = pid
        self.continuar = True
        self.action = env.process(self.iterar())

    def __repr__(self):
        return f"<{str(self.pid)}>"

    def send(self, mensaje:str):

    def recepcion(self):
        pass

    def computacion(self):
        pass

    def expulsion(self):
        pass

    def iterar(self):
        if continuar:
            self.recepcion()
            self.computacion()
            self.expulsion()
