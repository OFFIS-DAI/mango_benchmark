# given n agents, small world k, and an rng seed, output a
# small world topology of n agents
import random


def make_small_world_topology(n_agents, k, p, seed):
    # make 1:n_agents list of AIDs
    # make a ring
    # add additional connections to neighbours with distance <= k
    # add additional connections based on probability factor

    # from julia:
    # using PyCall
    # my_dir = @__DIR__
    # @pyinclude(my_dir * "/scenario_setup/make_topology.py")
    # py"make_small_world_topology(1,2,3,4)"

    # create a ring of size n_agents
    # and connect every k distance neighbors
    adjacency_matrix = [[0 for _ in range(n_agents)] for _ in range(n_agents)]

    for i in range(n_agents):
        for j in range(n_agents):
            if i == j:
                # agents are not their own neighbor
                continue

            if abs((i - j) % n_agents) <= k or abs(i - j) <= k:
                adjacency_matrix[i][j] = 1

    # add more edges with a random chance
    random.seed(seed)

    for i in range(n_agents):
        for j in range(i, n_agents):
            if i == j:
                # agents are not their own neighbor
                continue

            # ensure it stays symmetrical for convenience
            if adjacency_matrix[i][j] == 0:
                if random.random() < p:
                    adjacency_matrix[i][j] = 1
                    adjacency_matrix[j][i] = 1

    # output: n x n adjacency matrix
    return adjacency_matrix


if __name__ == "__main__":
    print(make_small_world_topology(10, 2, 0.5, 123))
