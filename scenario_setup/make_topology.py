# given n agents, small world k, and an rng seed, output a
# small world topology of n agents


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

    # output: n x n adjacency matrix
    return [
        [1, 2, 3, 4, 5, 6, 7, 8],
        [1, 2, 3, 4, 5, 6, 7, 8],
        [1, 2, 3, 4, 5, 6, 7, 8],
        [1, 2, 3, 4, 5, 6, 7, 8],
    ]
