import pygame
import json
import math
import random
from aco import ACOEngine
from weights_gen import generate_weights

pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w - 100, info.current_h - 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ACO Visualisation")

FONT = pygame.font.SysFont("Arial", 14)

# ---------------- CAMERA ----------------
zoom = 1.0
camera_offset = [WIDTH // 2, HEIGHT // 2]

def world_to_screen(x, y):
    if math.isnan(x) or math.isnan(y):
        return 0, 0
    return int(x * zoom + camera_offset[0]), int(y * zoom + camera_offset[1])

# ---------------- LOAD ----------------
def load_graph():
    with open("graph.json") as f:
        return json.load(f)

def load_or_generate_weights(graph, use_random):
    if use_random:
        print("Generating RANDOM weights...")
        return generate_weights(graph, randomize=True)

    try:
        with open("weights.json") as f:
            print("Loading weights.json...")
            return json.load(f)
    except:
        print("No weights.json → generating deterministic weights...")
        weights = generate_weights(graph, randomize=False)

        with open("weights.json", "w") as f:
            json.dump(weights, f, indent=2)

        return weights

def short_name(url):
    return url.split("/")[-1][:10]

# ---------------- SAFE LAYOUT ----------------
def generate_positions(graph, iterations=200):
    nodes = list(graph.keys())

    pos = {n: [random.uniform(-300, 300), random.uniform(-300, 300)] for n in nodes}

    for _ in range(iterations):
        disp = {n: [0, 0] for n in nodes}

        for v in nodes:
            for u in nodes:
                if u == v:
                    continue

                dx = pos[v][0] - pos[u][0]
                dy = pos[v][1] - pos[u][1]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist < 1e-5:
                    dx += random.uniform(-1,1)
                    dy += random.uniform(-1,1)
                    dist = 1

                force = 500 / dist
                disp[v][0] += (dx/dist) * force
                disp[v][1] += (dy/dist) * force

        for v in nodes:
            for u in graph[v]:
                dx = pos[v][0] - pos[u][0]
                dy = pos[v][1] - pos[u][1]
                dist = math.sqrt(dx*dx + dy*dy) + 1e-5

                force = (dist * dist) / 500
                disp[v][0] -= (dx/dist) * force
                disp[v][1] -= (dy/dist) * force

        for v in nodes:
            pos[v][0] += disp[v][0] * 0.01
            pos[v][1] += disp[v][1] * 0.01

            if math.isnan(pos[v][0]) or math.isnan(pos[v][1]):
                pos[v] = [random.uniform(-300,300), random.uniform(-300,300)]

    return {n:(p[0],p[1]) for n,p in pos.items()}

# ---------------- COLOR ----------------
def lerp_color(val, min_v, max_v):
    if max_v == min_v:
        t = 0
    else:
        t = (val - min_v)/(max_v - min_v)

    r = int(255*t)
    g = int(255*(1-abs(t-0.5)*2))
    b = int(255*(1-t))
    return (r,g,b)

# ---------------- DRAW ----------------
def draw_graph(graph, pos, tau, weights, source, target, visited):

    all_pher = [tau[u][v] for u in tau for v in tau[u]]
    min_p, max_p = min(all_pher), max(all_pher)

    for u in graph:
        for v in graph[u]:
            if u < v:
                x1,y1 = world_to_screen(*pos[u])
                x2,y2 = world_to_screen(*pos[v])

                pher = tau[u][v]
                color = lerp_color(pher, min_p, max_p)

                pygame.draw.line(screen, color, (x1,y1),(x2,y2),2)

                mx,my = (x1+x2)//2,(y1+y2)//2

                # pheromone (white)
                screen.blit(FONT.render(f"{pher:.2f}",True,(255,255,255)),(mx,my-10))

                # weight (pink)
                screen.blit(FONT.render(f"{weights[u][v]:.1f}",True,(255,100,200)),(mx,my+5))

    for node,(x,y) in pos.items():
        sx,sy = world_to_screen(x,y)

        if node==source:
            col=(0,255,0)
        elif node==target:
            col=(255,0,0)
        elif node in visited:
            col=(255,180,100)
        else:
            col=(100,100,100)

        pygame.draw.circle(screen,col,(sx,sy),14)
        screen.blit(FONT.render(short_name(node),True,(255,255,255)),(sx-20,sy-10))

# ---------------- ANTS ----------------
def draw_ants(ants,pos):
    for i,a in enumerate(ants):
        node = a["current"]
        x,y = world_to_screen(*pos[node])

        angle = (i/len(ants))*2*math.pi
        dx = int(math.cos(angle)*8)
        dy = int(math.sin(angle)*8)

        pygame.draw.circle(screen,(180,0,255),(x+dx,y+dy),4)

# ---------------- PROB ----------------
def draw_probabilities(probs,pos):
    for n,p in probs.items():
        x,y = world_to_screen(*pos[n])
        screen.blit(FONT.render(f"{p:.2f}",True,(255,255,255)),(x,y+15))

# ---------------- MAIN ----------------
def run_sim(graph, settings):

    nodes = list(graph.keys())
    source = nodes[0]
    target = nodes[-1]

    weights = load_or_generate_weights(graph, settings["random_weights"])
    settings["weights"] = weights

    aco = ACOEngine(
        graph, weights, source, target,
        alpha=settings["alpha"],
        beta=settings["beta"],
        rho=settings["rho"],
        Q=settings["Q"],
        num_ants=settings["num_ants"],
        max_steps=settings["max_steps"]
    )

    pos = generate_positions(graph)
    aco.initialize_ants()

    visited=set([source])

    iteration=0
    delay=200
    paused=True
    last=0

    global zoom, camera_offset

    clock = pygame.time.Clock()

    running=True
    while running:
        screen.fill((0,0,0))

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                return

            elif e.type==pygame.MOUSEBUTTONDOWN:
                if e.button==4: zoom*=1.1
                elif e.button==5: zoom/=1.1

            elif e.type==pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    camera_offset[0]+=e.rel[0]
                    camera_offset[1]+=e.rel[1]

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    paused = not paused

                elif e.key == pygame.K_UP:
                    delay = max(20, delay - 50)

                elif e.key == pygame.K_DOWN:
                    delay += 50

                elif e.key == pygame.K_r:
                    # reset simulation (same graph + settings)
                    return "reset"

                elif e.key == pygame.K_m:
                    # go back to menu
                    return "menu"

                elif e.key == pygame.K_ESCAPE:
                    return "quit"

        now = pygame.time.get_ticks()

        if not paused and now-last>delay:
            ants = aco.step_ants()
            last = now

            for a in ants:
                visited.update(a["visited"])
        else:
            ants = aco.ants

        draw_graph(graph,pos,aco.tau,weights,source,target,visited)
        draw_ants(ants,pos)

        # 🔥 show probabilities for ONE active ant
        for a in ants:
            if not a["finished"]:
                probs = aco.get_transition_probabilities(a["current"],a["visited"])
                draw_probabilities(probs,pos)
                break

        if all(a["finished"] for a in ants):
            aco.update_pheromones()
            aco.reset_ants()
            iteration+=1

        # HUD
        screen.blit(FONT.render(f"Iteration: {iteration}",True,(255,255,255)),(20,20))
        screen.blit(FONT.render(f"Speed: {delay} ms",True,(255,255,255)),(20,40))
        screen.blit(FONT.render(f"Zoom: {zoom:.2f}",True,(255,255,255)),(20,60))

        pygame.display.flip()
        clock.tick(60)

def run_menu():
    font = pygame.font.SysFont("Arial", 22)

    settings = {
        "alpha": 1,
        "beta": 1,
        "rho": 0.2,
        "Q": 1,
        "num_ants": 20,
        "max_steps": 20,
        "random_weights": True
    }

    keys = list(settings.keys())
    selected = 0

    running = True
    while running:
        screen.fill((20, 20, 20))

        title = font.render("ACO SETTINGS (ENTER to start)", True, (255,255,255))
        screen.blit(title, (50, 40))

        for i, k in enumerate(keys):
            val = settings[k]

            color = (255,255,0) if i == selected else (200,200,200)

            text = font.render(f"{k}: {val}", True, color)
            screen.blit(text, (50, 100 + i * 40))

        hint = font.render("↑ ↓ select | ← → change | ENTER start", True, (150,150,150))
        screen.blit(hint, (50, HEIGHT - 60))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(keys)

                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(keys)

                elif e.key == pygame.K_LEFT or e.key == pygame.K_RIGHT:
                    key = keys[selected]

                    if isinstance(settings[key], bool):
                        settings[key] = not settings[key]

                    elif isinstance(settings[key], int):
                        settings[key] += -1 if e.key == pygame.K_LEFT else 1

                    elif isinstance(settings[key], float):
                        settings[key] += -0.1 if e.key == pygame.K_LEFT else 0.1

                elif e.key == pygame.K_RETURN:
                    return settings
                
# ---------------- ENTRY ----------------
def main():
    graph = load_graph()

    while True:
        settings = run_menu()
        if settings is None:
            break

        # load weights based on toggle
        weights = load_or_generate_weights(graph, settings["random_weights"])
        settings["weights"] = weights

        result = run_sim(graph, settings)

        if result == "quit":
            break
        elif result == "menu":
            continue
        elif result == "reset":
            continue

    pygame.quit()

if __name__ == "__main__":
    main()