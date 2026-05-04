import requests
from bs4 import BeautifulSoup
from collections import deque
import json

BASE_URL = "https://en.wikipedia.org"

def get_valid_links(page_url, max_links):
    """Extract valid Wikipedia links from main content."""
    try:
        res = requests.get(
            page_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
        soup = BeautifulSoup(res.text, "html.parser")

        content = soup.find("div", id="mw-content-text")
        if content:
            content = content.find("div", class_="mw-parser-output")
        else:
            print(f"  [!] No content div found for {page_url}")
            return []

        links = []
        for p in content.find_all("p", class_=False, id_=False):
            if p.find_parent(["table"], class_=True):
                # most wikipedia pages have content inside p tags with no class names so they will be a direct descendent of mw-parser-output
                continue 
            for a in p.find_all("a", href=True):
                href = a["href"]
                # only valid wiki links, no need for images etc
                if href.startswith("/wiki/") and ":" not in href:
                    full_url = BASE_URL + href
                elif href.startswith("//en.wikipedia.org/wiki/") and ":" not in href:
                    full_url = href.replace("//en.wikipedia.org", BASE_URL) if not href.startswith("http") else href
                else:
                    continue
                if full_url not in links:
                    links.append(full_url)
                if len(links) >= max_links:
                    return links
        return links

    except Exception as e:
        print(f"Error fetching {page_url}: {e}")
        return []


def build_graph(start_url, max_nodes, max_links_per_page):
    """Build adjacency list using BFS crawl."""
    graph = {}
    visited = set()
    queue = deque([start_url])

    while queue and len(visited) < max_nodes:
        current = queue.popleft()
        if current in visited:
            continue
        print(f"Visiting: {current}")
        visited.add(current)
        neighbors = get_valid_links(current, max_links_per_page)
        graph[current] = neighbors
        for link in neighbors:
            if link not in visited and len(visited) + len(queue) < max_nodes:
                queue.append(link)

    # since graph is partially expanded we gotta remove edges to nodes not in graph
    graph_nodes = set(graph.keys())
    for node in graph:
        graph[node] = [nbr for nbr in graph[node] if nbr in graph_nodes]

    # modeling the graph as undirected to allow ants to move back and forth
    for node in list(graph.keys()):
        for nbr in graph[node]:
            if node not in graph[nbr]:
                graph[nbr].append(node)

    return graph

def check_path_exists_bfs(graph, start, target):
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        node, path = queue.popleft()
        if node == target:
            return path
        if node in visited:
            continue
        visited.add(node)
        for nbr in graph[node]:
            if nbr not in visited:
                queue.append((nbr, path + [nbr]))

    return None


if __name__ == "__main__":
    start = "https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms"
    try:
        with open("graph.json", "r") as f:
            graph = json.load(f)
        print("Loaded graph from file")
    except:
        graph = build_graph(start, max_nodes=50, max_links_per_page=12)
        with open("graph.json", "w") as f:
            json.dump(graph, f, indent=2)
        print("Graph built and saved")

    print("\n--- GRAPH BUILT ---")
    for node, neighbors in list(graph.items()):
        print(f"{node} -> {len(neighbors)} links")
    
    with open("graph.json", "w") as f:
        json.dump(graph, f, indent=2)

    print("Graph saved to graph.json")

    nodes = list(graph.keys())

    source = nodes[0]
    target = nodes[-1]   # or pick manually

    path = check_path_exists_bfs(graph, source, target)

    if path:
        print("\nBFS Path Found:")
        print(" -> ".join(path))
    else:
        print("\nNo path exists between source and target.")