# Ant Colony Optimisation (ACO)

- ACO is a probabilistic technique for solving computational problems that can be reduced to finding good paths through graphs.
- Biologists have observed that in the wild, many social insects find paths by something known as **stigmergy** - a mechanism of indirect coordination where agents (animals, robots, or humans) interact by modifying their environment, leaving traces that stimulate subsequent actions. 
- Real ants perform stigmergy by leaving **_pheromones_** when foraging - a behaviour where they spread out from the nest to search for food sources and bring food back to the nest. 
- Consider an experiment conducted by biologists on an _Argentine ant species_ where the ant nest was separated from a food source by a bridge with two branches - $l_s$ and $l_l$. In this experiment a variable $r = l_l/l_s$ was considered which was the ratio of the longer branch to the shorter branch. This variable $r$ was adjusted throughout the experiment epochs. Upon running the experiment multiple times, it was observed that the ants tend to converge to the shortest branch of the bridge with a high probability. At the start, each branch has no pheromone and thus an ant has no preference to choosing a branch. Each branch has an equal probability of being chosen by the ants. It chooses a branch at random. 
- On its way along the branch to the food source and back, the ant releases pheromones. These pheromones are then used by other ants to pick the branch. In social insects like ants, the better path is chosen based on stigmergy. The ants find more amount of the chemical pheromone on one of the branches and choose that branch. Pheromones also evaporate/decay over time, hence the branch with the shorter distance will have more pheromone concentration as the ant was able to complete its to-and-fro journey quicker. Since, successive ants choose the branch with the greater pheromone concentration greater number of trips are completed on that branch leading to an increase in pheromone concentration. This process creates a **positive feedback loop**, where the branch with higher pheromone concentration attracts more ants, which in turn leads to more pheromone deposit.
- Pheromone evaporation presents an issue with it, a strong pheromone trail on a branch can cause this ant system to get stuck in a suboptimal path.
- A crucial point to consider is that for an optimal shortest path from nest to food source the ants must deposit pheromones both on the journey to the food source and back to the nest. Failing to do so, will result in the convergence to a suboptimal path.
- The idea behind ant algorithms is then to use a form of artificial stigmergy to coordinate societies of artificial
agents. One of the most successful examples of ant algorithms is known as Ant Colony Optimization, or ACO. 

## The algorithm
TODO: (describe the algorithm here)


## This application
- ```wikiGraph.py``` graphs a subset of wikipedia
- ```aoc.py``` will run aoc on this graph
- ```visualise.py``` will run the visualisation of this aoc

## References
- https://web2.qatar.cmu.edu/~gdicaro/15382/additional/aco-book.pdf