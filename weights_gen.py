import json
import random
import argparse


def generate_weights(graph, randomize=False, low=1, high=5):
    weights = {}

    for u in graph:
        weights[u] = {}
    
    for u in graph:
        for v in graph[u]:
            if v in weights and u in weights[v]:
                weights[u][v] = weights[v][u]
            else:
                w = random.randint(low, high) if randomize else 1
                weights[u][v] = w
                weights[v][u] = w

    return weights


def save_weights(weights, filename="weights.json"):
    with open(filename, "w") as f:
        json.dump(weights, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--random", action="store_true")
    args = parser.parse_args()

    with open("graph.json") as f:
        graph = json.load(f)

    weights = generate_weights(graph, randomize=args.random)
    save_weights(weights)

    print("weights.json generated")