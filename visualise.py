import json
from aco import ACOEngine
from weights_gen import generate_weights


def load_graph():
    with open("graph.json") as f:
        return json.load(f)


def load_or_generate_weights(graph, use_random=False):
    try:
        with open("weights.json") as f:
            return json.load(f)
    except:
        print("No weights.json found → generating...")
        return generate_weights(graph, randomize=use_random)


def short_name(url):
    return url.split("/")[-1]


def run_simulation():
    graph = load_graph()

    # --- hyperparameters ---
    alpha = 1
    beta = 1
    rho = 0.2
    Q = 1
    num_ants = 30
    max_steps = 20
    iterations = 50

    use_random_weights = False
    weights = load_or_generate_weights(graph, use_random_weights)

    nodes = list(graph.keys())
    source = nodes[0]
    target = nodes[-1]

    print(f"\nSource: {short_name(source)}")
    print(f"Target: {short_name(target)}\n")

    aco = ACOEngine(
        graph, weights, source, target,
        alpha=alpha, beta=beta,
        rho=rho, Q=Q,
        num_ants=num_ants,
        max_steps=max_steps
    )

    for i in range(iterations):
        state = aco.step()

        print(f"\n=== Iteration {i} ===")

        # --- best path ---
        best = state["best_path"]
        if best:
            print(f"Best path length: {len(best) - 1}")
        else:
            print("No path found yet")

        # --- success stats ---
        success_count = sum(1 for a in state["ants"] if a["path"])
        print(f"Successful ants: {success_count}/{num_ants}")

        # --- START NODE PROBABILITIES (THIS IS THE IMPORTANT PART) ---
        start_probs = state.get("start_probabilities", {})

        if start_probs:
            print("\nTransition probabilities from SOURCE:")

            # sort by probability (descending for clarity)
            sorted_probs = sorted(
                start_probs.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for node, prob in sorted_probs:
                print(f"  {short_name(node):30} → {prob:.3f}")

        else:
            print("\nNo valid transitions from source")

        print("-" * 50)
        final_best = aco.best_path

        print("\n" + "=" * 60)
    print("FINAL BEST PATH:\n")

    if final_best:
        readable_path = " → ".join(short_name(n) for n in final_best)
        print(readable_path)
        print(f"\nPath length: {len(final_best) - 1}")
    else:
        print("No path found.")


if __name__ == "__main__":
    run_simulation()