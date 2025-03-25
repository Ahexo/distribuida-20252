import simpy


# Funcion para enviar un mensaje ya sea GO o BACK
def envia_msg(env, msg, receiver):
    sender = msg[3]
    peso = grafica[sender][receiver]
    store = stores[receiver]
    # print(f"Ronda {env.now}: {sender} envia {msg} a {receiver}")
    yield env.timeout(peso)
    yield store.put(msg)


# Funcion que corre para cada proceso
def proceso(env, id, vecinos, store):
    parent = None
    level = None
    while True:
        yield env.timeout(1)
        msg, dist, resp, pj = yield store.get()
        if msg == "GO":
            if parent is None:
                parent = pj
                print(f"Ronda {env.now}: p{parent} se convierte en padre de p{id}")
                children = []
                level = dist + 1
                expected_msg = len(vecinos) - 1
                if expected_msg == 0:
                    msg = ("BACK", dist + 1, "yes", id)
                    env.process(envia_msg(env, msg, parent))
                else:
                    for k in vecinos:
                        if k != pj:
                            msg = ("GO", dist + 1, None, id)
                            env.process(envia_msg(env, msg, k))
            elif level > dist + 1:
                parent = pj
                print(f"Ronda {env.now}: p{parent} se convierte en padre de p{id}")
                children = []
                level = dist + 1
                expected_msg = len(vecinos) - 1
                if expected_msg == 0:
                    msg = ("BACK", level, "yes", id)
                    env.process(envia_msg(env, msg, parent))
                else:
                    for k in vecinos:
                        if k != pj:
                            msg = ("GO", dist + 1, None, id)
                            env.process(envia_msg(env, msg, k))
            else:
                msg = ("BACK", dist + 1, "no", id)
                env.process(envia_msg(env, msg, pj))

        elif msg == "BACK":
            if dist == level + 1:
                if resp == "yes":
                    children.append(pj)
                expected_msg = expected_msg - 1
                if expected_msg == 0:
                    if parent != id:
                        msg = ("BACK", level, "no", id)
                        env.process(envia_msg(env, msg, parent))
                    else:
                        print(f"p{id} El arbol bfs se ha construido")
                        print(f"{parents = }")
                        print(f"{levels = }")

        parents[id] = parent
        levels[id] = level


def start(env, id):
    msg = ("GO", -1, None, id)
    env.process(envia_msg(env, msg, id))


# Matriz de adjacencias de la grafica
grafica = [
    [0, 2, 1, 0, 0, 0],
    [2, 0, 3, 0, 0, 0],
    [1, 3, 0, 3, 1, 0],
    [0, 0, 3, 0, 1, 1],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0],
]

n = len(grafica)

env = simpy.Environment()
# Usamos la clase Store para manejar el envio de mensajes entre los procesos
stores = [simpy.Store(env) for _ in range(n)]
# Estos dos diccionarios solo sirven para saber como esta construido el arbol al final
parents = {i: None for i in range(n)}
levels = {i: None for i in range(n)}
# Obten los vecinos de cada proceso i a partir de la matriz de adjacencias
vecinos = [[i for i in range(n) if row[i] != 0] for row in grafica]

# Determina el proceso distinguido segun la entrada del usuario
try:
    p_inicio = int(input("Escoge el proceso distinguido(0-5): "))
    if p_inicio > 5 or p_inicio < 0:
        raise Exception
except Exception:
    print("Escoge un numero entre 0 y 5")
    exit()

for i in range(n):
    env.process(proceso(env, i, vecinos[i], stores[i]))

start(env, p_inicio)

env.run(until=20)
