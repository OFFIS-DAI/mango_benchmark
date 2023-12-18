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

DUMMY_PORT = 5550
PORTS_START = 5555
HOST = ip"127.0.0.1"

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
    containers = Vector{Container}()
    agents = Vector{SimAgent}()

    n_containers = length(agent_lists)

    # TODO implement me


    return (agents, containers)
end

function container_to_agents(config::Dict{String,Any})::Vector{Vector{Int64}}
    # returns the agents IDs associated with each container as a vector of int vectors
    # each int value is an agent ID, the position in the top level vector corresponds to
    # the container number.
    n_agents = config["number_of_agents"]
    n_containers = config["number_of_containers"]
    agents_per_container = ceil(Int64, n_agents / n_containers)
    output = Vector{Vector{Int64}}()

    for _ in 1:n_containers
        push!(output, Vector{Int64}())
    end

    for i = 1:n_agents
        # 1:agents_per_container map to 1
        # n_agents+1:2*agents_per_container map to 2
        # ...
        container_id = ceil(Int64, i/agents_per_container)
        push!(output[container_id], i)
    end


    return output
end


function run_dummy()
    c1 = Container()
    c1.protocol = TCPProtocol(address = InetAddr(HOST, DUMMY_PORT))
    a1 = SimAgent(
        0.0,
        0.0,
        10,
        0.0,
        10,
        10,
        Vector{AgentAddress}(),
        Dict{AgentAddress,Threads.Condition}(),
        4,
        0,
    )
    register(c1, a1)

    c2 = Container()
    c2.protocol = TCPProtocol(address = InetAddr(HOST, DUMMY_PORT + 1))
    a2 = SimAgent(
        0.0,
        0.0,
        10,
        0.0,
        10,
        10,
        Vector{AgentAddress}(),
        Dict{AgentAddress,Threads.Condition}(),
        4,
        0,
    )
    register(c2, a2)

    a2_address = AgentAddress(c2.protocol.address, a2.aid)
    a1.neighbors = [a2_address]

    a1_address = AgentAddress(c1.protocol.address, a1.aid)
    a2.neighbors = [a1_address, a2_address]

    containers = [c1, c2]
    agents = [a1, a2]

    for c in containers
        wait(Threads.@spawn start(c))
    end

    @sync for a in agents
        @async run_agent(a)
    end

    @sync for c in containers
        @async shutdown(c)
    end
end

function run_simulation(config::Dict{String,Any})::Float64
    # adjacency_matrix = get_topology(config)
    # agent_lists = container_to_agents(config)
    # agents, containers = make_agents_and_containers(adjacency_matrix, agent_lists)
    # tik
    # start containers
    # start agents
    # wait for all agents to terminate
    # tok
    # shut down all containers
    # output time

    # get compilation times out of the measurement
    @time run_dummy()


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
        2,
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
        2,
        0,
    )
    register(c2, a2)

    a2_address = AgentAddress(c2.protocol.address, a2.aid)
    a1.neighbors = [a2_address]

    a1_address = AgentAddress(c1.protocol.address, a1.aid)
    a2.neighbors = [a1_address]

    containers = [c1, c2]
    agents = [a1, a2]


    start_time = time()

    for c in containers
        wait(Threads.@spawn start(c))
    end

    @sync for a in agents
        @async run_agent(a)
    end

    @sync for c in containers
        @async shutdown(c)
    end

    end_time = time()

    return end_time - start_time
end

function save_sim_results(times::Vector{Float64}, scenario_name::String)::Nothing
    # TODO implement me
    return nothing
end


function main()
    n_runs, configs = read_parameters()

    for config in configs
        result_times = zeros(Float64, n_runs)

        for i = 1:n_runs
            result_times[i] = run_simulation(config)
        end

        save_sim_results(result_times, configs["simulation_name"])
    end
end


main()