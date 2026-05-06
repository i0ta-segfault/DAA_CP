# Ant Colony Optimisation (ACO)

- ACO is a probabilistic technique for solving computational problems that can be reduced to finding good paths through graphs.
- Biologists have observed that in the wild, many social insects find paths by something known as **stigmergy** - a mechanism of indirect coordination where agents (animals, robots, or humans) interact by modifying their environment, leaving traces that stimulate subsequent actions. 
- Real ants perform stigmergy by leaving **_pheromones_** when foraging - a behaviour where they spread out from the nest to search for food sources and bring food back to the nest. 
- Consider an experiment conducted by biologists on an _Argentine ant species_ where the ant nest was separated from a food source by a bridge with two branches - $l_s$ and $l_l$. In this experiment a variable $r = l_l/l_s$ was considered which was the ratio of the longer branch to the shorter branch. This variable $r$ was adjusted throughout the experiment epochs. Upon running the experiment multiple times, it was observed that the ants tend to converge to the shortest branch of the bridge with a high probability. At the start, each branch has no pheromone and thus an ant has no preference to choosing a branch. Each branch has an equal probability of being chosen by the ants. It chooses a branch at random. 
- On its way along the branch to the food source and back, the ant releases pheromones. These pheromones are then used by other ants to pick the branch. In social insects like ants, the better path is chosen based on stigmergy. The ants find more amount of the chemical pheromone on one of the branches and choose that branch. Pheromones also evaporate/decay over time, hence the branch with the shorter distance will have more pheromone concentration as the ant was able to complete its to-and-fro journey quicker. Since, successive ants choose the branch with the greater pheromone concentration greater number of trips are completed on that branch leading to an increase in pheromone concentration. This process creates a **positive feedback loop**, where the branch with higher pheromone concentration attracts more ants, which in turn leads to more pheromone deposit.
- Pheromone evaporation presents an issue with it, a strong pheromone trail on a branch can cause this ant system to get stuck in a suboptimal path.
- A crucial point to consider is that for an optimal shortest path from nest to food source, in real life, the ants must deposit pheromones both on the journey to the food source and back to the nest. Failing to do so, will result in the convergence to a suboptimal path.
- In ACO we deposit pheromone along the entire constructed path.
- The idea behind ant algorithms is then to use a form of artificial stigmergy to coordinate societies of artificial
agents. One of the most successful examples of ant algorithms is known as Ant Colony Optimization, or ACO. 

## The algorithm
- An ant at a node connected to more nodes has a choice to make. 

```md
            B
          /
---------A----D
          \
            C

```
1. The probability that an ant will choose one of the nodes from the options it has is given by :
```math
P^k_{ij} =
\begin{cases}
\frac{(\tau_{ij})^\alpha (\eta_{ij})^\beta}
{\sum_{l \in N_i^k} (\tau_{il})^\alpha (\eta_{il})^\beta}
& \text{if } j \in N_i^k \\

0 & \text{otherwise}
\end{cases}
```

-   where :
    - $\tau$ indicates the pheromone level deposited on graph edges
    - $\eta$ indicates the heuristic information / desirability of a move between two points
    - $\alpha$ determines the influence of pheromone level in the algorithm
    - $\beta$ determines the influence of the heuristic importance  


2. Similarly the pheromone level $\tau$ is indicated by
```math
\tau_{ij} \leftarrow (1 - \rho)\tau_{ij} + \sum_{k=1}^{m} \Delta \tau_{ij}^k
```

- where:
  - $\rho$ is the evaporation rate  
  - $m$ is the number of ants  
  - $\Delta \tau_{ij}^k$ is the pheromone deposited by ant $k$  

- The pheromone deposited is defined as:

```math
\Delta \tau_{ij}^k =
\begin{cases}
\frac{Q}{L_k} & \text{if ant } k \text{ used edge } (i,j) \\

0 & \text{otherwise}
\end{cases}
```

- where:
  - $Q$ is a constant  
  - $L_k$ is the total length (cost) of the path constructed by ant $k$  


3. The heuristic information $\eta$ is given by 
```math
\eta_{ij} = \frac{1}{d_{ij}}
```

- where:
  - $d_{ij}$ is the cost (or weight) of edge $(i,j)$  

## This application
- ```wikiGraph.py``` graphs a subset of wikipedia
- ```aco.py``` will run aoc on this graph
- ```graphics_visualise.py``` will run the visualisation of this aoc
- ```weights_gen.py``` for the sake of visualisation of aoc this file can generate a random weight matrix
- ```graph.json``` the unweighted bidirectional graph ```wikiGraph.py``` spits out
---
1. ```wikiGraph.py``` will generate the partially expanded bidirectional unweighted graph of some wikipedia pages
2. ```graphics_visualise.py``` drives the sim loop and invokes ```aco.py``` for each step to demonstrate ant movement, pheromone deposits and the optimal path
3. ```graphics_visualise.py``` will, based on user input will send $\rightarrow$ hyperparameters $\rho$ (pheromone evaporation rate), $Q$ (pheromone deposit scale - a constant), $\alpha$ (pheromone importance), $\beta$ ($\eta$ heuristic importance), $m$ (the number of ants), $S_m$ (maximum number of steps) and a randomised $W_{ij}$ (the weights matrix)
    > The weights matrix $W_{ij}$ is technically always sent to the ```aco.py```. However, since this graph is modeling Wikipedia pages, two linked pages are technically always one click / one hop away and thus the edge weight between them stays one. Hence the $W_{ij}$ matrix is just a $J$ matrix.
    
    > But, to demonstrate how some arbitrary weights, if assumed, in this graph would affect the behaviour of the ants an option is presented to the user. Choosing that, ```weights_gen.py``` will generate a completely random weights matrix $W_{ij}$ which ```aco.py``` will then use for the algorithm.

4. ```weights.json``` the weights ```weights_gen.py``` generates. Useful for user inspection and general debugging
---
- Run ```pip install -r requirements.txt```
- Run ```python wikiGraph.py``` to create ```graph.json```
- Run ```graphics_visualise.py``` to run the simulation. Press M key to go back to menu, R to reset, Arrow keys UP and DOWN to manage speed and the SPACEBAR to pause/resume the simulation.

## Time Complexity
- In this application at any given node we can assume the node degree to be $d$. So the cost of computing probabilities becomes $O(d)$ per step
- For $S_m$ steps it will be $O(S_m * d)$
- This is done for all $m$ ants so $O(m * S_m * d)$
- For every edge we iterate over it to simulate pheromone evaporation : $O(E)$
- For every edge a successfult ant deposits pheromone along the edge : $O(S_m * m)$
- Combining it all the time complexity boils down to : $O(N * S_m * d + E)$ for each iteration
- For $I$ iterations the complexity will be $O(I(N * S_m * d + E))$

## Space Complexity
- We store the graph as an adjacency list : $O(V + E)$
- We store pheromone for every edge : $O(E)$
- We store weights for every edge : $O(E)$
- Each ant also stores the current node, the path. Assuming worst case of $S_m$ path length for $N$ ants : $O(N * S_m)$
- Total space complexity : $O(V + E + N * S_m)$

## References
- https://web2.qatar.cmu.edu/~gdicaro/15382/additional/aco-book.pdf
