import random

class ACOEngine:
    def __init__(self, graph, weights, source, target,
                 alpha=1, beta=1, rho=0.2, Q=1,
                 num_ants=15, max_steps=20):

        self.graph = graph
        self.weights = weights
        self.source = source
        self.target = target

        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q
        self.num_ants = num_ants
        self.max_steps = max_steps

        # initialise the pheromone matrix
        self.tau = {
            u: {v: 1.0 for v in graph[u]}
            for u in graph
        }

        self.best_path = None
        self.ants = []

    # js for pretty printing, ts gives the probability at each node
    def get_transition_probabilities(self, node, visited):
        neighbors = self.graph[node]
        candidates = [n for n in neighbors if n not in visited]

        if not candidates:
            return {}

        numerators = []
        for nbr in candidates:
            pher = self.tau[node][nbr] ** self.alpha
            eta = (1 / self.weights[node][nbr]) ** self.beta
            numerators.append(pher * eta)

        denom = sum(numerators)
        if denom == 0:
            return {}

        probabilities = [num / denom for num in numerators]

        return {
            nbr: prob for nbr, prob in zip(candidates, probabilities)
        }

    # for cli testing
    def construct_path(self):
        current = self.source
        path = [current]
        visited = set([current])

        while current != self.target and len(path) < self.max_steps:
            probs = self.get_transition_probabilities(current, visited)
            if not probs:
                break

            nodes = list(probs.keys())
            probabilities = list(probs.values())

            r = random.random()
            cumulative = 0
            next_node = nodes[-1]

            for node, prob in zip(nodes, probabilities):
                cumulative += prob
                if r <= cumulative:
                    next_node = node
                    break

            path.append(next_node)
            visited.add(next_node)
            current = next_node

        if current == self.target:
            return path
        return None

    def step(self):
        paths = []
        ants = []

        for _ in range(self.num_ants):
            path = self.construct_path()

            ants.append({
                "path": path if path else [],
                "current": path[-1] if path else self.source
            })

            if path:
                paths.append(path)

        # best path update
        if paths:
            best_iter = min(paths, key=lambda p: len(p))
            if self.best_path is None or len(best_iter) < len(self.best_path):
                self.best_path = best_iter

        # sim pheromone evaporation as per equn
        for u in self.tau:
            for v in self.tau[u]:
                self.tau[u][v] *= (1 - self.rho)

        # sim pheromone deposit as per equn
        for path in paths:
            L = sum(self.weights[path[i]][path[i+1]] for i in range(len(path)-1))
            if L <= 0:
                continue

            delta = self.Q / L

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.tau[u][v] += delta
                self.tau[v][u] += delta

        start_probs = self.get_transition_probabilities(self.source, {self.source})

        return {
            "pheromone": self.tau,
            "ants": ants,
            "best_path": self.best_path,
            "start_probabilities": start_probs
        }

    # only for graphics visualiser
    def initialize_ants(self):
        self.ants = [
            {
                "current": self.source,
                "visited": set([self.source]),
                "path": [self.source],
                "finished": False,
                "steps": 0
            }
            for _ in range(self.num_ants)
        ]

    def move_ant(self, ant):
        if ant["finished"]:
            return

        current = ant["current"]

        if current == self.target:
            ant["finished"] = True
            return

        if ant["steps"] >= self.max_steps:
            ant["finished"] = True
            return

        probs = self.get_transition_probabilities(current, ant["visited"])

        if not probs:
            ant["finished"] = True
            return

        nodes = list(probs.keys())
        probabilities = list(probs.values())

        r = random.random()
        cumulative = 0
        next_node = nodes[-1]

        for node, prob in zip(nodes, probabilities):
            cumulative += prob
            if r <= cumulative:
                next_node = node
                break

        ant["current"] = next_node
        ant["visited"].add(next_node)
        ant["path"].append(next_node)
        ant["steps"] += 1

        if next_node == self.target:
            ant["finished"] = True

    def step_ants(self):
        for ant in self.ants:
            self.move_ant(ant)
        return self.ants

    def update_pheromones(self):
        # sim pheromone evaporation as per equn
        for u in self.tau:
            for v in self.tau[u]:
                self.tau[u][v] *= (1 - self.rho)

        # deposit from successful ants
        for ant in self.ants:
            if ant["current"] != self.target:
                continue

            path = ant["path"]
            L = sum(self.weights[path[i]][path[i+1]] for i in range(len(path)-1))
            if L <= 0:
                continue

            delta = self.Q / L

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.tau[u][v] += delta
                self.tau[v][u] += delta

            # update best path
            if self.best_path is None or len(path) < len(self.best_path):
                self.best_path = path

    def reset_ants(self):
        self.initialize_ants()