module InputParser
using PyCall
using JSON

THIS_DIR = @__DIR__
PARAM_FILE = THIS_DIR * "/../scenario_setup/parameters.json"
PY_MAKE_TOPOLOGY = THIS_DIR * "/../scenario_setup/make_topology.py"

export read_parameters, get_topology

function read_parameters()::Tuple{Int64,Vector{Dict{String,Any}}}
    configs = JSON.parsefile(PARAM_FILE)
    return (configs["n_runs"], configs["simulation_configs"])
end

function get_topology(config::Dict{String,Any})::Matrix{Int64}
    number_of_agents = config["number_of_agents"]
    k = config["small_world_k"]
    p = config["small_world_p"]
    seed = config["rng_seed"]

    @pyinclude(PY_MAKE_TOPOLOGY)
    params = "$number_of_agents, $k, $p, $seed"
    python_call = "make_small_world_topology($params)"
    adjacency_matrix = py"$$python_call"

    return adjacency_matrix
end

end
