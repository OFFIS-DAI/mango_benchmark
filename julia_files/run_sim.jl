using Mango
using Sockets: InetAddr, @ip_str

using FromFile
@from "input_parser.jl" using InputParser
@from "sim_agent.jl" using SimulationAgent

function make_agents_and_containers(
    adjacency_matrix::Matrix{Int64},
    agent_lists::Vector{Vector{Int64}},
)::Tuple{Vector{SimAgent},Vector{Container}}
    # <adjacency_matrix> - symmetrical matrix of neighborhoods for n_agents
    # 0 - no connection, 1 - connection
    #
    # <agent_lists>
    # list of agent_ids (as int) for each container
    # contains as many lists as containers
    # container 1 takes list 1s agents, etc.

    # TODO implement me
end

function container_to_agents(config::Dict{String,Any})::Vector{Vector{Int64}}
    # TODO implement me
    return [[1]]
end


function run_simulation(config::Dict{String,Any})::Float64
    adjacency_matrix = get_topology(config)
    agent_lists = container_to_agents(config)
    # agents, containers = make_agents_and_containers(adjacency_matrix, agent_lists)

    simulation_time = 0.0
    # tik
    # start containers
    # start agents
    # wait for all agents to terminate
    # tok
    # shut down all containers
    # output time

    container = Container()
    container.protocol = TCPProtocol(address = InetAddr(ip"127.0.0.1", 2980))
    my_agent = SimAgent(
        0.0,
        0.0,
        10,
        0.0,
        10,
        10,
        Vector{AgentAddress}(),
        Dict{AgentAddress,Condition}(),
    )
    register(container, my_agent)

    return simulation_time
end


function main()
    configs = read_parameters()

    for config in configs
        run_simulation(config)
    end
end


main()