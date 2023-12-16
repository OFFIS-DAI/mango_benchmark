using Revise
using Mango
using Sockets: InetAddr, @ip_str

# using FromFile
# @from "input_parser.jl" using InputParser
# @from "sim_agent.jl" using SimulationAgent

import Mango.AgentCore.handle_message
include("sim_agent.jl")
include("input_parser.jl")
using .SimulationAgent
using .InputParser

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

    c1 = Container()
    c1.protocol = TCPProtocol(address = InetAddr(ip"127.0.0.1", 2980))
    a1 = SimAgent(
        0.0,
        0.0,
        10,
        0.0,
        10,
        10,
        Vector{AgentAddress}(),
        Dict{AgentAddress,Threads.Condition}(),
        0,
    )
    register(c1, a1)

    c2 = Container()
    c2.protocol = TCPProtocol(address = InetAddr(ip"127.0.0.1", 2981))
    a2 = SimAgent(
        0.0,
        0.0,
        10,
        0.0,
        10,
        10,
        Vector{AgentAddress}(),
        Dict{AgentAddress,Threads.Condition}(),
        0,
    )
    register(c2, a2)

    containers = [c1, c2]
    agents = [a1, a2]

    for c in containers
        wait(Threads.@spawn start(c))
    end

    a2_address = AgentAddress(c2.protocol.address, a2.aid)
    a1.neighbors = [a2_address]

    a1_address = AgentAddress(c1.protocol.address, a1.aid)
    a2.neighbors = [a1_address]

    @sync for a in agents
        @async run_agent(a)
    end

    for a in agents
        println(a.incoming_msg_count)
    end

    @sync for c in containers
        @async shutdown(c)
    end

    return simulation_time
end


function main()
    configs = read_parameters()

    for config in configs
        run_simulation(config)
    end
end


main()