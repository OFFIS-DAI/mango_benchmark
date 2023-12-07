module InputParser
using PyCall
using JSON

THIS_DIR = @__DIR__
PARAM_FILE = THIS_DIR * "../scenario_setup/parameters.json"
PY_MAKE_TOPOLOGY = THIS_DIR * "../scenario_setup/make_topology.py"

export read_parameters, get_topology, agent_container_map

function read_parameters()::Vector{Dict{String,Any}}
    configs = JSON.parsefile(PARAM_FILE)
    return configs["simulation_configs"]
end

function get_topology(config::Dict{String,Any})::Matrix{Int64}
    n_agents = config["n_agents"]
    k = config["small_world_k"]
    p = config["small_world_p"]
    seed = config["rng_seed"]

    @pyinclude(PY_MAKE_TOPOLOGY)
    params = "$n_agents, $k, $p, $seed"
    adjacency_matrix = py"make_small_world_topology($params)"

    return adjacency_matrix
end

function container_to_agents(config::Dict{String,Any})::Vector{Vector{Int64}}
    # TODO implement me
end

end
